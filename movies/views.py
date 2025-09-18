from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.db.models import Count
from django.contrib.auth.decorators import login_required


def index(request):
    search_term = request.GET.get("search")

    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data["title"] = "Movies"
    template_data["movies"] = movies
    return render(request, "movies/index.html", {"template_data": template_data})


def show(request, id):
    movie = Movie.objects.get(id=id)
    # Fetch top-level reviews (parent is null) and prefetch replies
    reviews = (
        Review.objects.filter(movie=movie, parent__isnull=True)
        .annotate(likes_count=Count("likes"))
        .order_by("-likes_count", "-date")
        .select_related("user")
        .prefetch_related("likes", "replies__user", "replies__likes")
    )
    template_data = {}
    template_data["title"] = movie.name
    template_data["movie"] = movie
    template_data["reviews"] = reviews
    return render(request, "movies/show.html", {"template_data": template_data})


@login_required
def create_review(request, id):
    if request.method == "POST" and request.POST["comment"] != "":
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST["comment"]
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect("movies.show", id=id)

    else:
        return redirect("movies.show", id=id)


@login_required
def create_reply(request, id, review_id):
    """Create a reply to an existing review (one-level threading).

    POST params: comment
    """
    if request.method == "POST" and request.POST.get("comment"):
        movie = Movie.objects.get(id=id)
        parent_review = get_object_or_404(Review, id=review_id, movie=movie)
        reply = Review()
        reply.comment = request.POST["comment"]
        reply.movie = movie
        reply.user = request.user
        reply.parent = parent_review
        reply.save()

    return redirect("movies.show", id=id)


@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user != review.user:
        return redirect("movies.show", id=id)

    if request.method == "GET":
        template_data = {}
        template_data["title"] = "Edit Review"
        template_data["review"] = review
        return render(
            request, "movies/edit_review.html", {"template_data": template_data}
        )

    elif request.method == "POST" and request.POST["comment"] != "":
        review = Review.objects.get(id=review_id)
        review.comment = request.POST["comment"]
        review.save()
        return redirect("movies.show", id=id)
    else:
        return redirect("movies.show", id=id)


@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    review.delete()

    return redirect("movies.show", id=id)

@login_required
def like_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Toggle like: if user already liked the review, remove it; otherwise add it
    if request.user in review.likes.all():
        review.likes.remove(request.user)
    else:
        review.likes.add(request.user)

    return redirect("movies.show", id=id)


# Note: unlike/dislike feature removed. Likes are toggled via `like_review`.