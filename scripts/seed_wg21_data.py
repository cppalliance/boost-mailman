#!/usr/bin/env python
"""Additive, richer HyperKitty seed for local UI development.

Ported from wg21-mailman's scripts/seed_dev_data.py. Creates threaded
discussions (nested replies) with distinct participants, votes, tags,
favorites, attachments, last-views, sender ids, a private list, an inactive
list and a demo login user.

Unlike the original it never deletes anything: messages already archived are
skipped as duplicates, and votes/tags/favorites/last-views are only added to
threads created by the current run, so re-running is safe.
"""

import argparse
import hashlib
import os
import random
import sys
import uuid
from datetime import timedelta
from email.message import EmailMessage
from urllib.error import HTTPError

import django
from mailmanclient import MailmanConnectionError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from allauth.account.models import EmailAddress  # noqa: E402
from django.conf import settings  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.utils import timezone  # noqa: E402
from django_mailman3.lib.mailman import get_mailman_client  # noqa: E402

from hyperkitty.lib.analysis import compute_thread_order_and_depth  # noqa: E402
from hyperkitty.lib.incoming import DuplicateMessage, add_to_list  # noqa: E402
from hyperkitty.lib.mailman import import_list_from_mailman  # noqa: E402
from hyperkitty.models import (  # noqa: E402
    Email,
    Favorite,
    LastView,
    MailingList,
    Sender,
    Tag,
    Tagging,
    Thread,
)

SAMPLE_TOPICS = [
    "Formal review of proposed Boost.Graph2 library",
    "Boost 1.87 release candidate testing",
    "Question about Boost.Asio strand semantics",
    "RFC: move CI from Travis to GitHub Actions",
    "Bug report: regression in Boost.Json parser",
    "Weekly release status update",
    "Call for comments on the new documentation toolchain",
    "Reminder: merge window closes Friday",
    "Summary of the Boost.Beast review discussion",
    "Patch available for Boost.Filesystem on Windows",
]

SAMPLE_NAMES = [
    ("Alice Chen", "alice@example.com"),
    ("Bob Martinez", "bob@example.com"),
    ("Carol Nguyen", "carol@example.com"),
    ("David Kim", "david@example.com"),
    ("Elena Rossi", "elena@example.com"),
    ("Frank O'Brien", "frank@example.com"),
    ("Grace Patel", "grace@example.com"),
    ("Henry Wilson", "henry@example.com"),
    ("Iris Johnson", "iris@example.com"),
    ("James Lopez", "james@example.com"),
    ("Karen Schmidt", "karen@example.com"),
    ("Leo Thompson", "leo@example.com"),
]

SAMPLE_TAGS = [
    "review",
    "bug",
    "patch",
    "release",
    "question",
    "announcement",
    "design",
    "performance",
]

LIST_META = {
    "boost-users": ("Boost Users", "Help and discussion for users of Boost libraries"),
    "boost-interest": ("Boost Interest", "Gauging interest in new library ideas"),
    "boost-announce": ("Boost Announce", "Low-volume release and review announcements"),
    "boost-testing": ("Boost Testing", "Regression testing and CI coordination"),
    "boost-docs": ("Boost Docs", "Documentation tooling and content"),
    "boost-steering": ("Boost Steering (Private)", "Private steering committee discussion"),
    "boost-langbinding": ("Boost Langbinding", "Archived list with no recent activity"),
}

DEFAULT_LISTS = ",".join(LIST_META)

# Local parts (without @domain) used to exercise HyperKitty index filters.
PRIVATE_LIST_PARTS = frozenset({"boost-steering"})
INACTIVE_LIST_PARTS = frozenset({"boost-langbinding"})

# Distinguishes these Message-IDs from scripts/seed_dev_data.py's so both
# seeds can target the same list without colliding.
MSGID_TAG = "rich"

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo"
DEMO_EMAIL = "demo@example.com"
DEMO_NAME = "Demo User"


def stable_mailman_id(email: str) -> str:
    """Fallback id when Mailman Core is unavailable."""
    digest = hashlib.sha1(email.encode("utf-8")).hexdigest()
    return str(uuid.UUID(digest[:32]))


def ensure_mailman_user(email: str, display_name: str) -> str:
    """Create/fetch a Mailman user and return its user_id."""
    try:
        client = get_mailman_client()
        try:
            mm_user = client.get_user(email)
        except HTTPError as exc:
            if exc.code != 404:
                raise
            mm_user = client.create_user(email, display_name)
        for address in mm_user.addresses:
            if str(address) == email and not address.verified:
                address.verify()
        return str(mm_user.user_id)
    except (HTTPError, MailmanConnectionError, OSError) as exc:
        print(f"  ! Mailman unavailable for {email}: {exc}")
        return stable_mailman_id(email)


def ensure_users() -> list:
    User = get_user_model()
    users = []
    for name, email in SAMPLE_NAMES:
        username = email.split("@", 1)[0].replace("'", "").replace(".", "")
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": name.split()[0],
                "last_name": " ".join(name.split()[1:]),
            },
        )
        if created:
            user.set_password("password")
            user.save()
            profile = user.hyperkitty_profile
            profile.karma = random.randint(1, 40)
            profile.save(update_fields=["karma"])
        EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={"verified": True, "primary": True},
        )
        users.append(user)

    demo, created = User.objects.get_or_create(
        username=DEMO_USERNAME,
        defaults={
            "email": DEMO_EMAIL,
            "first_name": "Demo",
            "last_name": "User",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        demo.set_password(DEMO_PASSWORD)
        demo.save()
        demo.hyperkitty_profile.karma = 25
        demo.hyperkitty_profile.save(update_fields=["karma"])
    EmailAddress.objects.get_or_create(
        user=demo,
        email=DEMO_EMAIL,
        defaults={"verified": True, "primary": True},
    )
    users.append(demo)
    return users


def list_local_part(list_addr: str) -> str:
    return list_addr.split("@", 1)[0]


def configure_core_list(list_addr: str, private: bool) -> None:
    """Push display name, description and archive policy into Mailman Core.

    HyperKitty copies these from Core (import_list_from_mailman and
    `manage.py mailman_sync`), so setting them only in HyperKitty would be
    reverted by the next sync.
    """
    display, description = LIST_META.get(
        list_local_part(list_addr), (None, None)
    )
    try:
        mm_list = get_mailman_client().get_list(list_addr)
    except (HTTPError, MailmanConnectionError, OSError) as exc:
        print(f"  ! Could not load {list_addr} from Mailman Core: {exc}")
        return
    if display:
        mm_list.settings["display_name"] = display
        mm_list.settings["description"] = description
    if private:
        mm_list.settings["archive_policy"] = "private"
    try:
        mm_list.settings.save()
    except (HTTPError, MailmanConnectionError, OSError) as exc:
        print(f"  ! Mailman rejected settings for {list_addr}: {exc}")


def subscribe_demo(list_addr: str) -> None:
    try:
        mm_list = get_mailman_client().get_list(list_addr)
        if not mm_list.is_member(DEMO_EMAIL):
            mm_list.subscribe(
                DEMO_EMAIL,
                DEMO_NAME,
                pre_verified=True,
                pre_confirmed=True,
                pre_approved=True,
            )
    except (HTTPError, MailmanConnectionError, OSError) as exc:
        print(f"  ! Could not subscribe {DEMO_EMAIL} to {list_addr}: {exc}")


def authors_for_thread(msg_count: int) -> list[tuple[str, str]]:
    """Pick distinct participants for a thread, always including the demo user."""
    pool = SAMPLE_NAMES[:]
    random.shuffle(pool)
    needed = min(msg_count, len(pool) + 1)
    authors = [(DEMO_NAME, DEMO_EMAIL)]
    for person in pool:
        if len(authors) >= needed:
            break
        authors.append(person)
    random.shuffle(authors)
    while len(authors) < msg_count:
        authors.append(random.choice(authors))
    return authors[:msg_count]


def message_id(list_addr: str, thread_idx: int, msg_idx: int) -> str:
    list_name, list_domain = list_addr.split("@", 1)
    return f"<{list_name}-{MSGID_TAG}-t{thread_idx}-m{msg_idx}@{list_domain}>"


def build_message(
    list_addr: str,
    thread_idx: int,
    msg_idx: int,
    parent_msg_idx: int | None,
    base_time,
    topic: str,
    author: tuple[str, str],
    with_attachment: bool,
) -> EmailMessage:
    name, addr = author
    msg = EmailMessage()
    list_name = list_local_part(list_addr)
    msg["From"] = f"{name} <{addr}>"
    msg["To"] = list_addr
    subject = f"[{list_name}] {topic} (thread {thread_idx + 1})"
    msg["Subject"] = subject if msg_idx == 0 else f"Re: {subject}"
    msg["Message-ID"] = message_id(list_addr, thread_idx, msg_idx)
    if parent_msg_idx is not None:
        parent_id = message_id(list_addr, thread_idx, parent_msg_idx)
        msg["In-Reply-To"] = parent_id
        msg["References"] = parent_id
    sent_at = base_time + timedelta(
        days=thread_idx % 20,
        hours=(thread_idx * 3 + msg_idx) % 24,
        minutes=msg_idx * 11,
    )
    msg["Date"] = sent_at.strftime("%a, %d %b %Y %H:%M:%S +0000")

    paragraphs = random.randint(2, 5)
    body_lines = [
        f"Message {msg_idx + 1} in thread {thread_idx + 1} on {list_addr}.",
        "",
    ]
    if msg_idx > 0:
        body_lines.extend(
            [
                f"> On thread {thread_idx + 1}, earlier writers said:",
                f"> Lorem ipsum dolor sit amet (quoted from message {parent_msg_idx + 1}).",
                "",
            ]
        )
    for p in range(paragraphs):
        body_lines.append(
            f"Paragraph {p + 1}: Lorem ipsum dolor sit amet, consectetur adipiscing "
            f"elit. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. "
            f"Thread {thread_idx + 1}, message {msg_idx + 1}."
        )
        body_lines.append("")
    if "patch" in topic.lower() or "bug" in topic.lower():
        body_lines.extend(
            [
                "```",
                "@@ -12,6 +12,9 @@ void example()",
                "     auto x = compute();",
                "+    // seed discussion patch",
                "+    x.normalize();",
                "     return x;",
                "```",
                "",
            ]
        )
    msg.set_content("\n".join(body_lines))

    if with_attachment:
        patch = (
            f"--- a/example.cpp\n+++ b/example.cpp\n"
            f"@@ thread {thread_idx + 1} message {msg_idx + 1} @@\n"
            f"+// seeded attachment for UI testing\n"
        ).encode("utf-8")
        msg.add_attachment(
            patch,
            maintype="text",
            subtype="x-diff",
            filename=f"thread-{thread_idx + 1}-msg-{msg_idx + 1}.patch",
        )
    return msg


def seed_list(list_addr: str, threads: int, replies: int) -> tuple[int, int, set]:
    """Archive messages; return (created, skipped, ids of newly created threads)."""
    created = 0
    skipped = 0
    new_thread_ids = set()
    # Keep discussions inside the overview "recent" window (~32 days).
    base_time = timezone.now() - timedelta(days=25)
    for thread_idx in range(threads):
        topic = random.choice(SAMPLE_TOPICS)
        authors = authors_for_thread(replies)
        for msg_idx in range(replies):
            if msg_idx == 0:
                parent_msg_idx = None
            elif msg_idx <= 2 or random.random() < 0.55:
                parent_msg_idx = 0
            else:
                parent_msg_idx = random.randint(0, msg_idx - 1)
            with_attachment = msg_idx > 0 and random.random() < 0.12
            msg = build_message(
                list_addr,
                thread_idx,
                msg_idx,
                parent_msg_idx,
                base_time,
                topic,
                authors[msg_idx],
                with_attachment,
            )
            try:
                add_to_list(list_addr, msg, from_import=True)
            except DuplicateMessage:
                skipped += 1
                continue
            created += 1
            if msg_idx == 0:
                root = Email.objects.get(
                    mailinglist__name=list_addr,
                    message_id=msg["Message-ID"].strip("<>"),
                )
                new_thread_ids.add(root.thread_id)
    return created, skipped, new_thread_ids


def link_senders() -> int:
    """Create Mailman users for the seed senders and store their user ids."""
    linked = 0
    name_by_address = {email: name for name, email in SAMPLE_NAMES}
    name_by_address[DEMO_EMAIL] = DEMO_NAME
    for sender in Sender.objects.filter(address__in=name_by_address):
        mailman_id = ensure_mailman_user(sender.address, name_by_address[sender.address])
        if sender.mailman_id != mailman_id:
            sender.mailman_id = mailman_id
            sender.save(update_fields=["mailman_id"])
            linked += 1
    return linked


def enrich_discussions(thread_ids: set, users: list) -> dict[str, int]:
    stats = {"votes": 0, "tags": 0, "favorites": 0, "last_views": 0}
    demo = next(u for u in users if u.username == DEMO_USERNAME)
    for thread in Thread.objects.filter(id__in=thread_ids):
        emails = list(thread.emails.order_by("date"))
        if not emails:
            continue

        # Popular tab needs votes_total > 0 on some threads.
        if random.random() < 0.55:
            for email in random.sample(emails, k=min(len(emails), random.randint(1, 3))):
                for user in random.sample(users, k=random.randint(1, min(4, len(users)))):
                    email.vote(random.choice([1, 1, 1, -1]), user)
                    stats["votes"] += 1

        if random.random() < 0.45:
            for tag_name in random.sample(SAMPLE_TAGS, k=random.randint(1, 3)):
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                Tagging.objects.get_or_create(
                    tag=tag, thread=thread, user=random.choice(users)
                )
                stats["tags"] += 1

        if random.random() < 0.35:
            Favorite.objects.get_or_create(thread=thread, user=demo)
            stats["favorites"] += 1
            if random.random() < 0.4:
                Favorite.objects.get_or_create(thread=thread, user=random.choice(users))
                stats["favorites"] += 1

        # Leave some threads unread for the demo user.
        if random.random() < 0.65:
            LastView.objects.update_or_create(
                thread=thread,
                user=demo,
                defaults={
                    "view_date": emails[-1].date - timedelta(hours=random.randint(1, 48))
                },
            )
            stats["last_views"] += 1

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--domain",
        default=os.environ.get("MAILMAN_DOMAIN", "lists.example.com"),
    )
    parser.add_argument(
        "--lists",
        default=os.environ.get("SEED_RICH_LISTS", DEFAULT_LISTS),
        help="Comma-separated local parts (without @domain); must exist in Core",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=int(os.environ.get("SEED_THREADS", "12")),
    )
    parser.add_argument(
        "--replies",
        type=int,
        default=int(os.environ.get("SEED_REPLIES", "5")),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=21,
        help="Random seed, so re-runs produce the same threads",
    )
    args = parser.parse_args()
    random.seed(args.seed)

    list_names = [f"{part.strip()}@{args.domain}" for part in args.lists.split(",")]

    users = ensure_users()
    settings.HYPERKITTY_BATCH_MODE = True

    total_created = 0
    total_skipped = 0
    total_enrich = {"votes": 0, "tags": 0, "favorites": 0, "last_views": 0}
    for list_addr in list_names:
        local_part = list_local_part(list_addr)
        private = local_part in PRIVATE_LIST_PARTS
        configure_core_list(list_addr, private)
        import_list_from_mailman(list_addr)
        if private:
            subscribe_demo(list_addr)

        if local_part in INACTIVE_LIST_PARTS:
            print(f"Seeding {list_addr} (inactive, no messages)...")
            continue

        print(f"Seeding {list_addr} ({args.threads} threads x {args.replies} messages)...")
        created, skipped, new_thread_ids = seed_list(list_addr, args.threads, args.replies)
        total_created += created
        total_skipped += skipped
        print(f"  +{created} messages ({skipped} skipped as duplicates)")
        enrich = enrich_discussions(new_thread_ids, users)
        for key, value in enrich.items():
            total_enrich[key] += value
        print(
            f"  +{enrich['votes']} votes, {enrich['tags']} tags, "
            f"{enrich['favorites']} favorites, {enrich['last_views']} last-views"
        )
        for thread in Thread.objects.filter(id__in=new_thread_ids):
            compute_thread_order_and_depth(thread)

    linked = link_senders()
    print(f"Linked {linked} senders to Mailman user ids")

    print("Warming caches...")
    for list_addr in list_names:
        if MailingList.objects.filter(name=list_addr).exists():
            call_command("hyperkitty_warm_up_cache", list_addr, verbosity=0)

    demo_posts = Email.objects.filter(sender__address=DEMO_EMAIL).count()
    print(
        f"Done: +{total_created} messages across {len(list_names)} lists, "
        f"{total_skipped} already present "
        f"({total_enrich['votes']} votes, {total_enrich['tags']} tags, "
        f"{total_enrich['favorites']} favorites, "
        f"{total_enrich['last_views']} last-views)."
    )
    print(f"Demo login: {DEMO_USERNAME} / {DEMO_PASSWORD} ({demo_posts} posts as participant)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
