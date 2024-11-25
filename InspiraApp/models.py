from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from shortuuid.django_fields import ShortUUIDField
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
import shortuuid

class User(AbstractUser):
    id = ShortUUIDField(primary_key=True, default=shortuuid.uuid)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="profile/", blank=True, null=True)
    location = models.CharField(max_length=150, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    
    def thumbnail(self):
        if self.avatar:
            return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 30px; object-fit: cover;" />' % (self.image))
        return "No image"
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["-created_at"]

def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)

def save_profile(sender, instance, *args, **kwargs):
    instance.profile.save()

post_save.connect(save_profile, sender=User)

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="category/", blank=True, null=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["-created_at"]

    
class Citation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="citations", blank=True, null=True)
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    author = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="citation/", blank=True, null=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Citation: {self.title} by {self.user.email}"
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Citation, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Citation"
        verbose_name_plural = "Citations"
        ordering = ["-created_at"]

    def like_count(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.id).count()

    def favorite_count(self):
        return Favorite.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.id).count()

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Permet de pointer vers un modèle
    object_id = object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")  # L'objet cible
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Favori de {self.user.email} pour {self.content_object}"
    
    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "content_type", "object_id"], name="unique_favorite")
        ]


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Like de {self.user.email} pour {self.content_object}"

    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "content_type", "object_id"], name="unique_like")
        ]


class Thought(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="thoughts", blank=True, null=True)
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    author = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="thought/", blank=True, null=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thought: {self.title} by {self.user.email}"

    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Thought, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "thought"
        verbose_name_plural = "thoughts"
        ordering = ["-created_at"]

    def like_count(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.id).count()

    def favorite_count(self):
        return Favorite.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.id).count()

class Paragraph(models.Model):
    thought = models.ForeignKey(Thought, on_delete=models.CASCADE, related_name="paragraphs")
    content = RichTextField()
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.thought.title
    
    class Meta:
        verbose_name = "Paragraph"
        verbose_name_plural = "Paragraphs"
        ordering = ["-created_at"]

class About(models.Model):
    title = models.CharField(max_length=150)
    description = RichTextField(blank=True)
    image = models.ImageField(upload_to="about/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "About"
        verbose_name_plural = "Abouts"
        ordering = ["-created_at"]
