#!/usr/bin/env python
"""Bulk seed HyperKitty archives for local UI development."""

import argparse
import os
import random
import sys
from datetime import timedelta
from email.message import EmailMessage

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.sites.models import Site  # noqa: E402
from django.utils import timezone  # noqa: E402

from hyperkitty.lib.incoming import DuplicateMessage, add_to_list  # noqa: E402

SAMPLE_TOPICS = [
    "Proposal for library feature X",
    "Meeting notes and action items",
    "Question about implementation details",
    "RFC: update the review process",
    "Bug report: regression in latest release",
    "Weekly status update",
    "Call for comments on draft specification",
    "Reminder: upcoming deadline",
    "Summary of mailing list discussion",
    "Patch available for testing",
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


def build_message(
    list_addr: str,
    thread_idx: int,
    msg_idx: int,
    base_time,
) -> EmailMessage:
    name, addr = random.choice(SAMPLE_NAMES)
    topic = random.choice(SAMPLE_TOPICS)
    msg = EmailMessage()
    msg_id = f"<{list_addr.split('@')[0]}-t{thread_idx}-m{msg_idx}@lists.example.com>"
    msg["From"] = f"{name} <{addr}>"
    msg["To"] = list_addr
    msg["Subject"] = f"[{list_addr.split('@')[0]}] {topic} (thread {thread_idx + 1})"
    msg["Message-ID"] = msg_id
    if msg_idx > 0:
        root_id = f"<{list_addr.split('@')[0]}-t{thread_idx}-m0@lists.example.com>"
        msg["In-Reply-To"] = root_id
        msg["References"] = root_id
    sent_at = base_time + timedelta(hours=thread_idx, minutes=msg_idx * 7)
    msg["Date"] = sent_at.strftime("%a, %d %b %Y %H:%M:%S +0000")
    paragraphs = random.randint(2, 5)
    body_lines = [
        f"Message {msg_idx + 1} in thread {thread_idx + 1} on {list_addr}.",
        "",
    ]
    for p in range(paragraphs):
        body_lines.append(
            f"Paragraph {p + 1}: Lorem ipsum dolor sit amet, consectetur adipiscing "
            f"elit. Integer posuere erat a ante venenatis dapibus posuere velit aliquet. "
            f"Thread {thread_idx + 1}, message {msg_idx + 1}."
        )
        body_lines.append("")
    msg.set_content("\n".join(body_lines))
    return msg


def seed_list(list_addr: str, threads: int, replies: int) -> tuple[int, int]:
    created = 0
    skipped = 0
    base_time = timezone.now() - timedelta(days=90)
    for thread_idx in range(threads):
        for msg_idx in range(replies):
            msg = build_message(list_addr, thread_idx, msg_idx, base_time)
            try:
                add_to_list(list_addr, msg, from_import=True)
                created += 1
            except DuplicateMessage:
                skipped += 1
    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--domain",
        default=os.environ.get("MAILMAN_DOMAIN", "lists.example.com"),
    )
    parser.add_argument(
        "--lists",
        default=os.environ.get(
            "SEED_LISTS",
            "delegates,paper-reviews,general,dev,announce,cpp,boost,test",
        ),
        help="Comma-separated local parts (without @domain)",
    )
    parser.add_argument("--threads", type=int, default=35)
    parser.add_argument("--replies", type=int, default=6)
    args = parser.parse_args()

    list_names = [f"{part.strip()}@{args.domain}" for part in args.lists.split(",")]

    Site.objects.update_or_create(
        pk=settings.SITE_ID,
        defaults={"domain": args.domain, "name": args.domain},
    )

    settings.HYPERKITTY_BATCH_MODE = True

    total_created = 0
    total_skipped = 0
    for list_addr in list_names:
        print(f"Seeding {list_addr} ({args.threads} threads x {args.replies} messages)...")
        created, skipped = seed_list(list_addr, args.threads, args.replies)
        total_created += created
        total_skipped += skipped
        print(f"  +{created} messages ({skipped} skipped as duplicates)")

    print(f"Done: {total_created} messages across {len(list_names)} lists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
