from app.models import Posts, Sites


def validate_post_site_ids(post: Posts, site: Sites) -> (str, bool):
    if post is None:
        msg = "A post with this id does not exist, or it does not belong to this sub site"
        return msg, False
    if site is None:
        msg = "This subsite does not exist"
        return msg, False
    if site.id != post.site_id:
        msg = "This post does not exist for this subsite"
        return msg, False

    return '', True
