from comment_service.schemas.comments import CommentVote


def convert_user_vote_to_value(vote: CommentVote) -> int:
    vote_val = 0
    if vote.vote == 'upvote':
        vote_val = 1
    elif vote.vote == 'downvote':
        vote_val = -1

    return vote_val
