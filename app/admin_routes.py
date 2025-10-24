import os
from datetime import datetime
from typing import List

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from . import db
from .models import (
    CATEGORY_CHOICES,
    Project,
    SiteSetting,
    User,
    update_project_images,
    slugify,
)


admin_bp = Blueprint("admin", __name__, template_folder="templates/admin")


def allowed_file(filename: str) -> bool:
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", set())


def save_file(file_storage) -> str | None:
    if file_storage and file_storage.filename and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        filename = f"{timestamp}_{filename}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file_storage.save(file_path)
        rel_path = os.path.relpath(file_path, current_app.static_folder)
        return rel_path.replace(os.sep, "/")
    return None


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("登录成功", "success")
            return redirect(url_for("admin.dashboard"))
        flash("用户名或密码错误", "danger")
    return render_template("admin/login.html")


@admin_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("您已退出登录", "info")
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    project_count = Project.query.count()
    settings = SiteSetting.query.first()
    return render_template(
        "admin/dashboard.html",
        project_count=project_count,
        settings=settings,
    )


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    settings = SiteSetting.query.first()
    if request.method == "POST":
        settings.hero_title = request.form.get("hero_title", settings.hero_title)
        settings.hero_subtitle = request.form.get("hero_subtitle", settings.hero_subtitle)
        settings.hero_cta_text = request.form.get("hero_cta_text", settings.hero_cta_text)
        settings.hero_cta_link = request.form.get("hero_cta_link", settings.hero_cta_link)
        settings.hero_secondary_cta_text = request.form.get(
            "hero_secondary_cta_text", settings.hero_secondary_cta_text
        )
        settings.hero_secondary_cta_link = request.form.get(
            "hero_secondary_cta_link", settings.hero_secondary_cta_link
        )
        settings.about_title = request.form.get("about_title", settings.about_title)
        settings.about_body = request.form.get("about_body", settings.about_body)
        settings.about_highlights = request.form.get(
            "about_highlights", settings.about_highlights
        )
        settings.innovation_title = request.form.get(
            "innovation_title", settings.innovation_title
        )
        settings.innovation_body = request.form.get(
            "innovation_body", settings.innovation_body
        )
        settings.insights_title = request.form.get("insights_title", settings.insights_title)
        settings.contact_business = request.form.get(
            "contact_business", settings.contact_business
        )
        settings.contact_recruit = request.form.get(
            "contact_recruit", settings.contact_recruit
        )
        settings.contact_general = request.form.get(
            "contact_general", settings.contact_general
        )
        settings.contact_address = request.form.get(
            "contact_address", settings.contact_address
        )
        settings.contact_phone = request.form.get("contact_phone", settings.contact_phone)

        db.session.commit()
        flash("站点信息已更新", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", settings=settings)


@admin_bp.route("/projects")
@login_required
def projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("admin/projects.html", projects=projects, categories=CATEGORY_CHOICES)


@admin_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category") or CATEGORY_CHOICES[0]
        slug = slugify(name or f"project-{datetime.utcnow().strftime('%H%M%S')}")
        cover_image_path = save_file(request.files.get("cover_image")) or "img/placeholder-16x9.svg"

        project = Project(name=name or slug, slug=slug, category=category, cover_image=cover_image_path)
        image_paths: List[str] = []
        for idx in range(1, 7):
            image_paths.append(
                save_file(request.files.get(f"image_{idx}")) or "img/placeholder-16x9.svg"
            )
        update_project_images(project, image_paths)

        db.session.add(project)
        db.session.commit()
        flash("案例已创建", "success")
        return redirect(url_for("admin.projects"))

    return render_template("admin/edit_project.html", project=None, categories=CATEGORY_CHOICES)


@admin_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id: int):
    project = Project.query.get_or_404(project_id)
    if request.method == "POST":
        project.name = request.form.get("name", project.name).strip() or project.name
        project.category = request.form.get("category", project.category)
        new_slug = request.form.get("slug", project.slug).strip() or project.slug
        if new_slug != project.slug:
            project.slug = slugify(new_slug)
        cover_upload = request.files.get("cover_image")
        cover_path = save_file(cover_upload)
        if cover_path:
            project.cover_image = cover_path

        updated_images: List[str] = []
        for idx, existing in enumerate(project.images, start=1):
            upload = request.files.get(f"image_{idx}")
            if upload and upload.filename:
                updated_images.append(save_file(upload) or existing.image_path)
            else:
                updated_images.append(existing.image_path)

        # Handle newly added slots if less than 6
        for idx in range(len(project.images) + 1, 7):
            upload = request.files.get(f"image_{idx}")
            if upload and upload.filename:
                updated_images.append(save_file(upload) or "img/placeholder-16x9.svg")
            else:
                updated_images.append("img/placeholder-16x9.svg")

        update_project_images(project, updated_images[:6])
        db.session.commit()
        flash("案例已更新", "success")
        return redirect(url_for("admin.projects"))

    return render_template(
        "admin/edit_project.html",
        project=project,
        categories=CATEGORY_CHOICES,
    )


@admin_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id: int):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("案例已删除", "info")
    return redirect(url_for("admin.projects"))
