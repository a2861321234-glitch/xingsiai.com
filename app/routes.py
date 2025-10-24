from collections import defaultdict
from datetime import datetime

from flask import Blueprint, abort, render_template

from .models import CATEGORY_CHOICES, Project, SiteSetting


main_bp = Blueprint("main", __name__)


@main_bp.context_processor
def inject_globals():
    settings = SiteSetting.query.first()
    return {
        "site_settings": settings,
        "nav_items": [
            {"label": "首页", "href": "#hero"},
            {"label": "关于形思", "href": "#about"},
            {"label": "设计案例", "href": "#cases"},
            {"label": "创新服务", "href": "#services"},
            {"label": "联系我们", "href": "#contact"},
        ],
        "now": datetime.utcnow,
    }


@main_bp.route("/")
def index():
    settings = SiteSetting.query.first()
    projects = Project.query.order_by(Project.created_at.desc()).all()

    grouped = defaultdict(list)
    for project in projects:
        grouped[project.category].append(project)

    return render_template(
        "index.html",
        settings=settings,
        projects=projects,
        grouped_projects=grouped,
        categories=CATEGORY_CHOICES,
    )


@main_bp.route("/projects/<slug>")
def project_detail(slug: str):
    project = Project.query.filter_by(slug=slug).first()
    if project is None:
        abort(404)
    return render_template("project_detail.html", project=project)
