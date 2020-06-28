import datetime
from sttapp.app import celery
from sttapp.proposals.models import Proposal
from sttapp.users.models import MyHistory


@celery.task()
def connect_member_and_history(event_id, proposal_id, event_title, event_real_days, link):

    proposal = Proposal.objects.get(id=proposal_id)
   
    for a in proposal.attendees:
        event_ids = a.event_ids
        event_ids.append(event_id)

        a.event_ids = event_ids
        a.updated_at = datetime.datetime.utcnow()
        a.save()

        if not a.user_id:
            continue
        h = MyHistory(
            user_id=a.user_id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            title=event_title,
            start_date=proposal.start_date,
            end_date=proposal.end_date,
            days=event_real_days,
            link=link,
            order=MyHistory.objects(user_id=a.user_id).order_by(
                '-order').first().order + 1
        )
        h.save()
