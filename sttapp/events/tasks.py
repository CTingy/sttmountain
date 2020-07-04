import datetime
import itertools
from sttapp.exts.celery  import celery
from sttapp.users.models import MyHistory
from sttapp.events.models import Event


def connect_to_member(attendees, event_id):

    for a in attendees:
        event_ids = a.event_ids
        event_ids.append(event_id)
        a.event_ids = event_ids
        a.updated_at = datetime.datetime.utcnow()
        a.save()


def connect_to_user_history(attendees, event, link):

    for a in attendees:
        if not a.user_id:
            continue
        last_history = MyHistory.objects(user_id=a.user_id).order_by('-order').first()
        h = MyHistory(
            user_id=a.user_id,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            title=event.title,
            start_date=event.proposal.start_date,
            end_date=event.proposal.end_date,
            days=event.days,
            link=link,
            order=last_history.order + 1 if last_history else 1
        )
        h.save()


@celery.task()
def connect_member_and_history(event_id, link):

    event = Event.objects.get(id=event_id)
    for_member_connection, for_history_connection = itertools.tee(event.proposal.attendees, 2)

    connect_to_member(for_member_connection, event_id)
    connect_to_user_history(for_history_connection, event, link)
