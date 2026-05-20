from core.datatables.views import BaseDataTableView

from ..models import (
    AchievementBadge,
    Challenge,
    ChallengeParticipant,
    ChallengeProgressLog,
    Leaderboard,
    MemberBadge,
    MemberReward,
    MemberStreak,
    Reward,
)


CHALLENGE_COLUMNS = [
    ("id", "id"),
    ("title", "title"),
    ("challenge_type", lambda obj: obj.get_challenge_type_display()),
    ("goal_target", "goal_target"),
    ("goal_unit", lambda obj: obj.get_goal_unit_display()),
    ("start_date", "start_date"),
    ("end_date", "end_date"),
    ("participation_type", lambda obj: obj.get_participation_type_display()),
    ("visibility", lambda obj: obj.get_visibility_display()),
    ("status", lambda obj: obj.get_status_display()),
]

CHALLENGE_PARTICIPANT_COLUMNS = [
    ("id", "id"),
    ("challenge", lambda obj: obj.challenge.title),
    ("member", lambda obj: str(obj.member)),
    ("joined_at", "joined_at"),
    ("current_progress", "current_progress"),
    ("completion_percentage", "completion_percentage"),
    ("current_rank", lambda obj: obj.current_rank or "-"),
    ("status", lambda obj: obj.get_status_display()),
]

CHALLENGE_PROGRESS_LOG_COLUMNS = [
    ("id", "id"),
    ("challenge_participant", lambda obj: str(obj.challenge_participant)),
    ("logged_at", "logged_at"),
    ("progress_value", "progress_value"),
    ("source_type", lambda obj: obj.get_source_type_display()),
]

LEADERBOARD_COLUMNS = [
    ("id", "id"),
    ("challenge", lambda obj: obj.challenge.title),
    ("generated_at", "generated_at"),
    ("member", lambda obj: str(obj.member)),
    ("rank_position", "rank_position"),
    ("score_value", "score_value"),
]

ACHIEVEMENT_BADGE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("badge_type", lambda obj: obj.get_badge_type_display()),
    ("criteria_value", "criteria_value"),
    ("status", lambda obj: obj.get_status_display()),
]

MEMBER_BADGE_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: str(obj.member)),
    ("achievement_badge", lambda obj: obj.achievement_badge.name),
    ("awarded_at", "awarded_at"),
    ("source_reference_type", lambda obj: obj.source_reference_type or "-"),
    ("source_reference_id", lambda obj: obj.source_reference_id or "-"),
]

MEMBER_STREAK_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: str(obj.member)),
    ("streak_type", lambda obj: obj.get_streak_type_display()),
    ("current_streak", "current_streak"),
    ("longest_streak", "longest_streak"),
    ("last_activity_date", lambda obj: obj.last_activity_date or "-"),
]

REWARD_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("reward_type", lambda obj: obj.get_reward_type_display()),
    ("points_required", lambda obj: obj.points_required if obj.points_required is not None else "-"),
    ("status", lambda obj: obj.get_status_display()),
]

MEMBER_REWARD_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: str(obj.member)),
    ("reward", lambda obj: obj.reward.name),
    ("redeemed_at", "redeemed_at"),
    ("status", lambda obj: obj.get_status_display()),
]


class ChallengeDataTableView(BaseDataTableView):
    model = Challenge
    columns = CHALLENGE_COLUMNS
    searchable_columns = ["title", "description", "challenge_type", "goal_unit", "status"]
    orderable_columns = ["id", "title", "challenge_type", "goal_target", "start_date", "end_date", "status"]


class ChallengeParticipantDataTableView(BaseDataTableView):
    model = ChallengeParticipant
    columns = CHALLENGE_PARTICIPANT_COLUMNS
    searchable_columns = ["challenge__title", "member__member_code", "member__party__name", "status"]
    orderable_columns = ["id", "challenge__title", "member__member_code", "joined_at", "current_progress", "completion_percentage", "current_rank", "status"]


class ChallengeProgressLogDataTableView(BaseDataTableView):
    model = ChallengeProgressLog
    columns = CHALLENGE_PROGRESS_LOG_COLUMNS
    searchable_columns = [
        "challenge_participant__challenge__title",
        "challenge_participant__member__member_code",
        "challenge_participant__member__party__name",
        "source_type",
        "notes",
    ]
    orderable_columns = ["id", "challenge_participant__challenge__title", "logged_at", "progress_value", "source_type"]


class LeaderboardDataTableView(BaseDataTableView):
    model = Leaderboard
    columns = LEADERBOARD_COLUMNS
    searchable_columns = ["challenge__title", "member__member_code", "member__party__name"]
    orderable_columns = ["id", "challenge__title", "generated_at", "member__member_code", "rank_position", "score_value"]


class AchievementBadgeDataTableView(BaseDataTableView):
    model = AchievementBadge
    columns = ACHIEVEMENT_BADGE_COLUMNS
    searchable_columns = ["name", "description", "badge_type", "status"]
    orderable_columns = ["id", "name", "badge_type", "criteria_value", "status"]


class MemberBadgeDataTableView(BaseDataTableView):
    model = MemberBadge
    columns = MEMBER_BADGE_COLUMNS
    searchable_columns = [
        "member__member_code",
        "member__party__name",
        "achievement_badge__name",
        "source_reference_type",
    ]
    orderable_columns = ["id", "member__member_code", "achievement_badge__name", "awarded_at", "source_reference_type", "source_reference_id"]


class MemberStreakDataTableView(BaseDataTableView):
    model = MemberStreak
    columns = MEMBER_STREAK_COLUMNS
    searchable_columns = ["member__member_code", "member__party__name", "streak_type"]
    orderable_columns = ["id", "member__member_code", "streak_type", "current_streak", "longest_streak", "last_activity_date"]


class RewardDataTableView(BaseDataTableView):
    model = Reward
    columns = REWARD_COLUMNS
    searchable_columns = ["name", "reward_type", "description", "status"]
    orderable_columns = ["id", "name", "reward_type", "points_required", "status"]


class MemberRewardDataTableView(BaseDataTableView):
    model = MemberReward
    columns = MEMBER_REWARD_COLUMNS
    searchable_columns = ["member__member_code", "member__party__name", "reward__name", "status"]
    orderable_columns = ["id", "member__member_code", "reward__name", "redeemed_at", "status"]
