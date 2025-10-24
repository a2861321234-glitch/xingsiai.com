import os
import random
import string
from datetime import datetime
from typing import List

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


CATEGORY_CHOICES = ["外观设计", "结构设计"]


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_title = db.Column(db.String(255), default="READY TO SHAPE THE FUTURE?")
    hero_subtitle = db.Column(db.Text, default="形思工业设计以创新驱动产品价值，帮助品牌跨越想象的边界。")
    hero_cta_text = db.Column(db.String(120), default="GET IN TOUCH")
    hero_cta_link = db.Column(db.String(255), default="#contact")
    hero_secondary_cta_text = db.Column(db.String(120), default="VIEW PROJECTS")
    hero_secondary_cta_link = db.Column(db.String(255), default="#cases")
    about_title = db.Column(db.String(255), default="关于形思")
    about_body = db.Column(
        db.Text,
        default=(
            "形思工业设计专注于未来工业体验，从趋势洞察到量产落地，"
            "我们以跨学科团队将复杂工程转化为优雅的产品体验。"
        ),
    )
    about_highlights = db.Column(
        db.Text,
        default="年度奖项 36+|专利成果 52|合作品牌 120+",
    )
    innovation_title = db.Column(db.String(255), default="创新服务")
    innovation_body = db.Column(
        db.Text,
        default=(
            "我们从战略规划、设计迭代到供应链协同提供全流程创新服务，"
            "以数据驱动决策，帮助客户快速验证市场机会。"
        ),
    )
    insights_title = db.Column(db.String(255), default="资讯洞察")
    contact_business = db.Column(db.String(255), default="biz@xingsi-design.com")
    contact_recruit = db.Column(db.String(255), default="hr@xingsi-design.com")
    contact_general = db.Column(db.String(255), default="hello@xingsi-design.com")
    contact_address = db.Column(db.String(255), default="上海市杨浦区设计大道88号")
    contact_phone = db.Column(db.String(64), default="+86 21 0000 0000")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(32), nullable=False)
    cover_image = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = db.relationship(
        "ProjectImage",
        backref="project",
        cascade="all, delete-orphan",
        order_by="ProjectImage.sort_order",
    )


class ProjectImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)


# Utility helpers

def random_suffix(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def slugify(name: str) -> str:
    base = (
        name.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("_", "-")
        .replace("?", "")
    )
    base = "".join(ch for ch in base if ch.isalnum() or ch == "-")
    base = base.strip("-") or random_suffix()
    candidate = base
    index = 1
    while Project.query.filter_by(slug=candidate).first() is not None:
        candidate = f"{base}-{index}"
        index += 1
    return candidate


def ensure_admin_account() -> None:
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")

    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()


def ensure_default_settings() -> None:
    if SiteSetting.query.first() is None:
        db.session.add(SiteSetting())
        db.session.commit()


def ensure_minimum_projects(target: int = 60) -> None:
    current = Project.query.count()
    if current >= target:
        return

    placeholder = "img/placeholder-16x9.svg"
    categories_cycle = CATEGORY_CHOICES * (target // len(CATEGORY_CHOICES) + 1)

    for index in range(current, target):
        name = f"概念产品 {index + 1:02d}"
        category = categories_cycle[index]
        slug = slugify(f"concept-{index + 1}")
        project = Project(name=name, slug=slug, category=category, cover_image=placeholder)
        for image_index in range(6):
            project.images.append(
                ProjectImage(
                    image_path=placeholder,
                    sort_order=image_index,
                )
            )
        db.session.add(project)

    db.session.commit()


def update_project_images(project: Project, image_paths: List[str]) -> None:
    project.images.clear()
    for order, path in enumerate(image_paths):
        if path:
            project.images.append(ProjectImage(image_path=path, sort_order=order))
    if not project.images:
        for order in range(6):
            project.images.append(
                ProjectImage(image_path="img/placeholder-16x9.svg", sort_order=order)
            )
