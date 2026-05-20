from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.challenge_data_table import (
    ACHIEVEMENT_BADGE_COLUMNS,
    CHALLENGE_COLUMNS,
    CHALLENGE_PARTICIPANT_COLUMNS,
    CHALLENGE_PROGRESS_LOG_COLUMNS,
    LEADERBOARD_COLUMNS,
    MEMBER_BADGE_COLUMNS,
    MEMBER_REWARD_COLUMNS,
    MEMBER_STREAK_COLUMNS,
    REWARD_COLUMNS,
    AchievementBadgeDataTableView,
    ChallengeDataTableView,
    ChallengeParticipantDataTableView,
    ChallengeProgressLogDataTableView,
    LeaderboardDataTableView,
    MemberBadgeDataTableView,
    MemberRewardDataTableView,
    MemberStreakDataTableView,
    RewardDataTableView,
)
from ...forms.challenge_form import (
    AchievementBadgeForm,
    ChallengeForm,
    ChallengeParticipantForm,
    ChallengeProgressLogForm,
    LeaderboardForm,
    MemberBadgeForm,
    MemberRewardForm,
    MemberStreakForm,
    RewardForm,
)
from ...models import (
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


def _title(key):
    return key.replace("_", " ").title()


register_entity(
    EntityConfig(
        name="challenge",
        url_path="challenges",
        verbose_name="Challenge",
        model=Challenge,
        form_class=ChallengeForm,
        datatable_view=ChallengeDataTableView,
        fields=[
            {"name": "title", "label": "Title", "type": "text", "required": True, "col": 6},
            {"name": "challenge_type", "label": "Challenge Type", "type": "static_select", "required": True, "col": 3, "options": [("", "Select Type"), *Challenge.ChallengeType.choices]},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 3, "options": [("", "Select Status"), *Challenge.Status.choices]},
            {"name": "goal_target", "label": "Goal Target", "type": "number", "required": True, "col": 3},
            {"name": "goal_unit", "label": "Goal Unit", "type": "static_select", "required": True, "col": 3, "options": [("", "Select Unit"), *Challenge.GoalUnit.choices]},
            {"name": "participation_type", "label": "Participation", "type": "static_select", "required": True, "col": 3, "options": [("", "Select Participation"), *Challenge.ParticipationType.choices]},
            {"name": "visibility", "label": "Visibility", "type": "static_select", "required": True, "col": 3, "options": [("", "Select Visibility"), *Challenge.Visibility.choices]},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": True, "col": 4},
            {"name": "end_date", "label": "End Date", "type": "date", "required": True, "col": 4},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[{"name": key, "title": _title(key)} for key, _accessor in CHALLENGE_COLUMNS if key != "id"],
        reset_defaults={"status": Challenge.Status.DRAFT, "visibility": Challenge.Visibility.PUBLIC, "participation_type": Challenge.ParticipationType.INDIVIDUAL},
        select_search_fields=["title", "challenge_type", "status"],
        select_label_func=lambda obj: f"{obj.title} ({obj.get_status_display()})",
    )
)

register_entity(
    EntityConfig(
        name="challenge_participant",
        url_path="challenge-participants",
        verbose_name="Challenge Participant",
        model=ChallengeParticipant,
        form_class=ChallengeParticipantForm,
        datatable_view=ChallengeParticipantDataTableView,
        fields=[
            {"name": "challenge", "label": "Challenge", "type": "select", "required": True, "col": 4, "url_name": "challenge_select"},
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "joined_at", "label": "Joined At", "type": "datetime-local", "required": True, "col": 4},
            {"name": "current_progress", "label": "Current Progress", "type": "number", "required": True, "col": 3},
            {"name": "completion_percentage", "label": "Completion %", "type": "number", "required": True, "col": 3},
            {"name": "current_rank", "label": "Current Rank", "type": "number", "required": False, "col": 3},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 3, "options": [("", "Select Status"), *ChallengeParticipant.Status.choices]},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[{"name": key, "title": _title(key)} for key, _accessor in CHALLENGE_PARTICIPANT_COLUMNS if key != "id"],
        reset_defaults={"status": ChallengeParticipant.Status.ACTIVE, "current_progress": 0, "completion_percentage": 0},
        select_search_fields=["challenge__title", "member__member_code", "member__party__name"],
        select_label_func=lambda obj: f"{obj.member} - {obj.challenge.title}",
    )
)

register_entity(
    EntityConfig(
        name="challenge_progress_log",
        url_path="challenge-progress-logs",
        verbose_name="Challenge Progress Log",
        model=ChallengeProgressLog,
        form_class=ChallengeProgressLogForm,
        datatable_view=ChallengeProgressLogDataTableView,
        fields=[
            {"name": "challenge_participant", "label": "Participant", "type": "select", "required": True, "col": 4, "url_name": "challenge_participant_select"},
            {"name": "logged_at", "label": "Logged At", "type": "datetime-local", "required": True, "col": 4},
            {"name": "progress_value", "label": "Progress Value", "type": "number", "required": True, "col": 4},
            {"name": "source_type", "label": "Source", "type": "static_select", "required": True, "col": 4, "options": [("", "Select Source"), *ChallengeProgressLog.SourceType.choices]},
            {"name": "notes", "label": "Notes", "type": "textarea", "required": False, "col": 8},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[{"name": key, "title": _title(key)} for key, _accessor in CHALLENGE_PROGRESS_LOG_COLUMNS if key != "id"],
        reset_defaults={"source_type": ChallengeProgressLog.SourceType.MANUAL},
        select_search_fields=["challenge_participant__challenge__title", "challenge_participant__member__member_code"],
        select_label_func=lambda obj: f"{obj.challenge_participant} - {obj.progress_value}",
    )
)

register_entity(
    EntityConfig(
        name="leaderboard",
        url_path="leaderboards",
        verbose_name="Leaderboard",
        model=Leaderboard,
        form_class=LeaderboardForm,
        datatable_view=LeaderboardDataTableView,
        fields=[
            {"name": "challenge", "label": "Challenge", "type": "select", "required": True, "col": 4, "url_name": "challenge_select"},
            {"name": "generated_at", "label": "Generated At", "type": "datetime-local", "required": True, "col": 4},
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "rank_position", "label": "Rank Position", "type": "number", "required": True, "col": 6},
            {"name": "score_value", "label": "Score Value", "type": "number", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[{"name": key, "title": _title(key)} for key, _accessor in LEADERBOARD_COLUMNS if key != "id"],
        select_search_fields=["challenge__title", "member__member_code", "member__party__name"],
        select_label_func=lambda obj: f"{obj.challenge.title} - Rank {obj.rank_position}",
    )
)

register_entity(
    EntityConfig(
        name="achievement_badge",
        url_path="achievement-badges",
        verbose_name="Achievement Badge",
        model=AchievementBadge,
        form_class=AchievementBadgeForm,
        datatable_view=AchievementBadgeDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4},
            {"name": "badge_type", "label": "Badge Type", "type": "static_select", "required": True, "col": 4, "options": [("", "Select Type"), *AchievementBadge.BadgeType.choices]},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 4, "options": [("", "Select Status"), *AchievementBadge.Status.choices]},
            {"name": "criteria_value", "label": "Criteria Value", "type": "number", "required": True, "col": 4},
            {"name": "icon", "label": "Icon", "type": "text", "required": False, "col": 8},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[{"name": key, "title": _title(key)} for key, _accessor in ACHIEVEMENT_BADGE_COLUMNS if key != "id"],
        reset_defaults={"status": AchievementBadge.Status.ACTIVE},
        select_search_fields=["name", "badge_type", "status"],
        select_label_func=lambda obj: obj.name,
    )
)

register_entity(
    EntityConfig(
        name="member_badge",
        url_path="member-badges",
        verbose_name="Member Badge",
        model=MemberBadge,
        form_class=MemberBadgeForm,
        datatable_view=MemberBadgeDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "achievement_badge", "label": "Achievement Badge", "type": "select", "required": True, "col": 4, "url_name": "achievement_badge_select"},
            {"name": "awarded_at", "label": "Awarded At", "type": "datetime-local", "required": True, "col": 4},
            {"name": "source_reference_type", "label": "Source Type", "type": "text", "required": False, "col": 6},
            {"name": "source_reference_id", "label": "Source ID", "type": "number", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[{"name": key, "title": _title(key)} for key, _accessor in MEMBER_BADGE_COLUMNS if key != "id"],
        select_search_fields=["member__member_code", "member__party__name", "achievement_badge__name"],
        select_label_func=lambda obj: f"{obj.member} - {obj.achievement_badge.name}",
    )
)

register_entity(
    EntityConfig(
        name="member_streak",
        url_path="member-streaks",
        verbose_name="Member Streak",
        model=MemberStreak,
        form_class=MemberStreakForm,
        datatable_view=MemberStreakDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "streak_type", "label": "Streak Type", "type": "static_select", "required": True, "col": 4, "options": [("", "Select Type"), *MemberStreak.StreakType.choices]},
            {"name": "last_activity_date", "label": "Last Activity Date", "type": "date", "required": False, "col": 4},
            {"name": "current_streak", "label": "Current Streak", "type": "number", "required": True, "col": 6},
            {"name": "longest_streak", "label": "Longest Streak", "type": "number", "required": True, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[{"name": key, "title": _title(key)} for key, _accessor in MEMBER_STREAK_COLUMNS if key != "id"],
        reset_defaults={"current_streak": 0, "longest_streak": 0},
        select_search_fields=["member__member_code", "member__party__name", "streak_type"],
        select_label_func=lambda obj: f"{obj.member} - {obj.get_streak_type_display()}",
    )
)

register_entity(
    EntityConfig(
        name="reward",
        url_path="rewards",
        verbose_name="Reward",
        model=Reward,
        form_class=RewardForm,
        datatable_view=RewardDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4},
            {"name": "reward_type", "label": "Reward Type", "type": "static_select", "required": True, "col": 4, "options": [("", "Select Type"), *Reward.RewardType.choices]},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 4, "options": [("", "Select Status"), *Reward.Status.choices]},
            {"name": "points_required", "label": "Points Required", "type": "number", "required": False, "col": 4},
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 8},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[{"name": key, "title": _title(key)} for key, _accessor in REWARD_COLUMNS if key != "id"],
        reset_defaults={"status": Reward.Status.ACTIVE},
        select_search_fields=["name", "reward_type", "status"],
        select_label_func=lambda obj: obj.name,
    )
)

register_entity(
    EntityConfig(
        name="member_reward",
        url_path="member-rewards",
        verbose_name="Member Reward",
        model=MemberReward,
        form_class=MemberRewardForm,
        datatable_view=MemberRewardDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "reward", "label": "Reward", "type": "select", "required": True, "col": 4, "url_name": "reward_select"},
            {"name": "redeemed_at", "label": "Redeemed At", "type": "datetime-local", "required": True, "col": 4},
            {"name": "status", "label": "Status", "type": "static_select", "required": True, "col": 12, "options": [("", "Select Status"), *MemberReward.Status.choices]},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[{"name": key, "title": _title(key)} for key, _accessor in MEMBER_REWARD_COLUMNS if key != "id"],
        reset_defaults={"status": MemberReward.Status.PENDING},
        select_search_fields=["member__member_code", "member__party__name", "reward__name", "status"],
        select_label_func=lambda obj: f"{obj.member} - {obj.reward.name}",
    )
)
