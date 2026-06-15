from datetime import date

from django.core.management.base import BaseCommand

from undecided_voters.models import RawPost, ScrapingRun, WeeklyAnalysis


STUB_WEEKS = [
    {
        "week_start": date(2024, 10, 21),
        "week_end": date(2024, 10, 28),
        "source": "newsapi",
        "total_posts_analyzed": 142,
        "reasons": {
            "unclear_policy_positions": "32%",
            "economic_concerns": "28%",
            "leadership_credibility": "18%",
            "party_loyalty_conflict": "12%",
            "foreign_policy_uncertainty": "10%",
        },
        "detailed_analysis": (
            "Voter uncertainty this week centers heavily on economic policy specifics. "
            "Many undecided voters express support for Harris's broad economic vision but "
            "want more concrete details on inflation relief and housing affordability. "
            "A secondary theme is leadership credibility, with swing-state voters citing "
            "her VP record as both a strength and a liability. Regional variation is "
            "notable: Midwestern voters focus on trade and manufacturing, while Sun Belt "
            "voters emphasize immigration and border policy."
        ),
        "supporting_evidence": {
            "unclear_policy_positions": [
                "I agree with her values but I still don't know exactly what she'd do on day one.",
                "Harris has talked a lot about affordability but the plan feels vague to me.",
                "Polling data shows 41% of independents say they want more policy specifics before deciding.",
            ],
            "economic_concerns": [
                "Grocery prices are still up 20% from 2021. I need to know she has a real fix.",
                "A Reuters/Ipsos poll found 63% of undecided voters rank the economy as their top concern.",
                "Small business owners in Ohio say they're waiting to see her tax plan details.",
            ],
            "leadership_credibility": [
                "She's been VP for four years — what has she actually changed?",
                "Experts note her handling of the border issue has been a consistent credibility challenge.",
                "Focus groups in Pennsylvania show mixed views on her debate performance vs. prior expectations.",
            ],
            "party_loyalty_conflict": [
                "I'm a lifelong Democrat but I'm not sure she's the right candidate right now.",
                "Some moderate Republicans say they'd consider Harris but can't get past the progressive platform.",
            ],
            "foreign_policy_uncertainty": [
                "Her stance on the Middle East conflict has shifted — I don't know where she really stands.",
                "Defense analysts say her foreign policy record is thin and hard to evaluate.",
            ],
        },
    },
    {
        "week_start": date(2024, 10, 14),
        "week_end": date(2024, 10, 21),
        "source": "newsapi",
        "total_posts_analyzed": 118,
        "reasons": {
            "media_coverage_bias": "30%",
            "policy_flip_flop_concerns": "25%",
            "economic_concerns": "22%",
            "demographic_representation": "13%",
            "debate_performance": "10%",
        },
        "detailed_analysis": (
            "This week's analysis reveals a surge in concerns about media framing of the Harris campaign. "
            "Many undecided voters feel they're getting an incomplete or partisan picture and are "
            "actively seeking alternative sources. Policy consistency is the second major theme — "
            "voters point to shifts on fracking, Medicare for All, and border policy as reasons for "
            "hesitation. Economic anxiety remains persistent but slightly down from the prior week."
        ),
        "supporting_evidence": {
            "media_coverage_bias": [
                "I feel like I can't get a straight story on her — every outlet spins it differently.",
                "A Gallup survey found 58% of independents distrust cable news coverage of the 2024 race.",
                "Voters in focus groups report turning to podcasts and local news for less partisan coverage.",
            ],
            "policy_flip_flop_concerns": [
                "She was against fracking in 2019 and now she's for it. Which is the real Harris?",
                "Policy analysts note at least four major position changes since her 2020 primary run.",
                "Medicare for All flip is the most cited example among undecided progressives.",
            ],
            "economic_concerns": [
                "Inflation is still my number one issue and I want to know her plan isn't just Biden 2.0.",
                "Wisconsin dairy farmers say trade policy consistency matters more than campaign promises.",
            ],
            "demographic_representation": [
                "As a Black voter I want to feel she's speaking to our community's specific challenges.",
                "Latino voter groups in Arizona say her outreach has improved but gaps remain.",
            ],
            "debate_performance": [
                "She did well in the debate but I want to see how she handles real hostile questioning.",
                "Post-debate polling showed a 6-point bump among college-educated women in swing states.",
            ],
        },
    },
    {
        "week_start": date(2024, 10, 7),
        "week_end": date(2024, 10, 14),
        "source": "twitter",
        "total_posts_analyzed": 203,
        "reasons": {
            "authenticity_concerns": "35%",
            "economic_concerns": "24%",
            "foreign_policy_uncertainty": "19%",
            "youth_voter_enthusiasm_gap": "14%",
            "healthcare_stance": "8%",
        },
        "detailed_analysis": (
            "Twitter sentiment analysis this week shows authenticity as the dominant concern. "
            "Undecided voters frequently question whether Harris's public persona reflects her "
            "genuine positions or is strategically managed. Economic anxiety is present but "
            "youth voters in particular are flagging an enthusiasm gap — they want to be excited "
            "but say the campaign messaging isn't landing. Foreign policy uncertainty is elevated "
            "following news coverage of the Middle East and NATO discussions."
        ),
        "supporting_evidence": {
            "authenticity_concerns": [
                "She laughs at weird moments and it makes me wonder if she's being coached too hard.",
                "I want to vote for her but her answers feel rehearsed, not genuine.",
                "Twitter threads analyzing her interview clips have millions of views from skeptical voters.",
            ],
            "economic_concerns": [
                "My rent went up 40% in three years. I need someone with a real housing plan.",
                "Gen Z voters on Twitter say student debt relief matters but isn't enough on its own.",
            ],
            "foreign_policy_uncertainty": [
                "She said she supports Israel then pivoted. I genuinely don't know where she stands.",
                "NATO allies quoted in the FT say they're watching Harris's positions closely.",
                "Undecided military family members cite foreign policy consistency as a key deciding factor.",
            ],
            "youth_voter_enthusiasm_gap": [
                "The Beyoncé endorsement was cool but I need policy, not vibes.",
                "Campus organizers in Michigan say turnout motivation is harder than 2020.",
                "A Harvard IOP poll found only 37% of under-30 voters feel 'enthusiastic' about Harris.",
            ],
            "healthcare_stance": [
                "She dropped Medicare for All and now I don't know what her actual healthcare plan is.",
                "Nurses unions in swing states say her current healthcare platform lacks specifics.",
            ],
        },
    },
]


class Command(BaseCommand):
    help = "Seed the database with stub WeeklyAnalysis data for UI development and screenshots"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing stub data before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            WeeklyAnalysis.objects.all().delete()
            ScrapingRun.objects.all().delete()
            RawPost.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing data."))

        created = 0

        for stub in STUB_WEEKS:
            _, was_created = WeeklyAnalysis.objects.update_or_create(
                week_start=stub["week_start"],
                week_end=stub["week_end"],
                source=stub["source"],
                defaults={
                    "total_posts_analyzed": stub["total_posts_analyzed"],
                    "reasons": stub["reasons"],
                    "detailed_analysis": stub["detailed_analysis"],
                    "supporting_evidence": stub["supporting_evidence"],
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created} new WeeklyAnalysis records ({len(STUB_WEEKS) - created} already existed)."
            )
        )
        self.stdout.write("View results at http://localhost:3001/analyses")
