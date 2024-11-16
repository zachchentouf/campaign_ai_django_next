# services/scraper.py
import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List

import openai
from asgiref.sync import async_to_sync
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from newsapi import NewsApiClient
from twikit import Client

from .models import RawPost, ScrapingRun, WeeklyAnalysis


class ContentScraper(ABC):
    """Abstract base class for content scrapers"""

    @abstractmethod
    async def init_client(self):
        pass

    @abstractmethod
    async def scrape(self, from_date=None, to_date=None):
        pass


class TwitterScraper(ContentScraper):
    def __init__(self):
        self.client = Client(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        self.search_terms = [
            "undecided voter",
            "can't decide who to vote for",
            "not sure who to vote for",
        ]

    async def init_client(self):
        await self.client.login(
            auth_info_1=settings.TWITTER_USERNAME,
            auth_info_2=settings.TWITTER_EMAIL,
            password=settings.TWITTER_PASSWORD,
        )

    async def scrape(self, from_date: datetime, to_date: datetime):
        await self.init_client()
        all_tweets = []
        for term in self.search_terms:
            tweets = await self.client.search_tweet(term, "Top", count=100)

            for tweet in tweets:
                # Parse Twitter's date format: 'Wed Oct 09 16:29:36 +0000 2024'
                if isinstance(tweet.created_at, str):
                    tweet_date = datetime.strptime(
                        tweet.created_at, "%a %b %d %H:%M:%S %z %Y"
                    )
                    # No need to make_aware since the date already includes timezone (+0000)
                else:
                    tweet_date = timezone.make_aware(tweet.created_at)

                # Apply date filtering if dates are provided
                if from_date <= tweet_date <= to_date:
                    all_tweets.append(
                        {
                            "text": tweet.text,
                            "created_at": tweet_date,
                            "author": tweet.user.name,
                            "publisher": None,
                            "metadata": {
                                "likes": tweet.favorite_count,
                                "retweets": tweet.retweet_count,
                            },
                        }
                    )
                

        return all_tweets


class NewsAPIScraper(ContentScraper):
    def __init__(self):
        self.api_key = settings.NEWSAPI_KEY
        self.newsapi = NewsApiClient(api_key=self.api_key)
        # specifying Harris so that it is in the US
        self.search_terms = [
            "Harris undecided voter",
            "Harris undecided voters",
            "Harris voter uncertainty",
        ]

    async def init_client(self):
        pass

    async def scrape(self, from_date: datetime, to_date: datetime):
        """Scrape NewsAPI for undecided voter content"""
        all_articles = []

        # Convert dates to ISO format if provided
        from_param = from_date.strftime("%Y-%m-%d") 
        to_param = to_date.strftime("%Y-%m-%d")

        for term in self.search_terms:
            for page in range(1, 2):  # Pages 1-10
                articles = self.newsapi.get_everything(
                    q=term,
                    from_param=from_param,
                    to=to_param,
                    language="en",
                    sort_by="relevancy",
                    page_size=50,
                    page=page,
                )

                if articles["status"] == "ok":
                    if not articles["articles"]:  # No more articles available
                        break

                    for article in articles["articles"]:
                        all_articles.append(
                            {
                                "text": f"{article['title']} - {article['description']}",
                                "created_at": datetime.strptime(
                                    article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                                ),
                                "author": article.get("author", "Unknown"),
                                "publisher": article["source"][
                                    "name"
                                ],  # New field for news outlet
                                "metadata": {
                                    "url": article["url"],
                                    "urlToImage": article.get("urlToImage"),
                                },
                            }
                        )

        return all_articles


class UndecidedVoterAnalyzer:
    def __init__(self):
        self.openai = openai
        self.openai.api_key = settings.OPENAI_API_KEY
        self.scrapers = {"twitter": TwitterScraper(), "newsapi": NewsAPIScraper()}

    @transaction.atomic
    def run_scraping_sync(self, source: str, from_date: str, to_date: str) -> List[ScrapingRun]:
        """Run scraping synchronously
        
        Args:
            source: Data source identifier
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            List of completed ScrapingRun instances
        """
        # Convert string dates to aware datetime objects
        from_date_datetime = datetime.strptime(from_date, "%Y-%m-%d")
        to_date_datetime = datetime.strptime(to_date, "%Y-%m-%d")
        from_date_aware = timezone.make_aware(from_date_datetime)
        to_date_aware = timezone.make_aware(to_date_datetime)
        
        sources_to_scrape = list(self.scrapers.keys()) if source == "all" else [source]
        all_runs = []

        for src in sources_to_scrape:
            scraping_run = ScrapingRun.objects.create(
                status="RUNNING",
                source=src,
                date_range_start=from_date_aware,
                date_range_end=to_date_aware,
            )

            try:
                items = async_to_sync(self.scrapers[src].scrape)(from_date_aware, to_date_aware)

                for item in items:
                    RawPost.objects.create(
                        scraping_run=scraping_run,
                        source=src,
                        content=item["text"],
                        post_date=item["created_at"],
                        author=item["author"],
                        metadata=item.get("metadata", {}),
                        publisher=item.get("publisher", None),
                    )

                scraping_run.status = "COMPLETED"
                scraping_run.total_posts_scraped = len(items)
                scraping_run.end_time = timezone.now()
                scraping_run.save()

            except Exception as e:
                scraping_run.status = "FAILED"
                scraping_run.error_message = str(e)
                scraping_run.end_time = timezone.now()
                scraping_run.save()
                raise e

            all_runs.append(scraping_run)

        return all_runs

    def analyze_week(self, week_start_date: str, source: str) -> None:
        """Analyze posts for a given week
        
        Args:
            week_start_date: Start date in YYYY-MM-DD format
            source: Data source identifier
        """
        # Convert string date to aware datetime
        week_start = timezone.make_aware(
            datetime.strptime(week_start_date, "%Y-%m-%d")
        )
        week_end = week_start + timedelta(days=7)

        # Get posts for the week and source
        posts_query = RawPost.objects.filter(
            post_date__range=[week_start, week_end]
        )

        if source != "all":
            posts_query = posts_query.filter(source=source)

        posts = posts_query.all()

        if not posts:
            print(f"No posts found for source {source} in date range")
            return

        # Prepare content for OpenAI with approximate token limit
        # Estimate tokens using chars/4 (rough approximation)
        
        # TODO: Can implement batch analysis to avoid token limit
        content_parts = []
        total_chars = 0
        char_limit = 7000 * 4  # ~32000 chars for 8000 tokens
        
        for post in posts:
            if total_chars + len(post.content) > char_limit:
                break
            content_parts.append(post.content)
            total_chars += len(post.content)
        
        content = "\n".join(content_parts)

        try:
            # OpenAI analysis
            twitter_prompt = """You are an expert political analyst. Your task is to analyze social media posts specifically about voter uncertainty regarding Kamala Harris.

For each set of tweets, you must return a JSON object with this exact structure:
{
    "reasons": {
        "reason1": "percentage1",  # e.g. "unclear_stance_on_policies": "35%"
        "reason2": "percentage2"
    },
    "quotes": {
        "reason1": ["tweet1", "tweet2"],  # Direct quotes from tweets supporting each reason
        "reason2": ["tweet1", "tweet2"]
    },
    "summary": "brief analysis focusing on why voters are uncertain about supporting or opposing Kamala Harris"
}

Focus specifically on:
- Voters' perceptions of Harris's policies and positions
- Concerns about her leadership capabilities
- Reactions to her performance as Vice President
- Comparisons to other potential candidates
- Personal or demographic factors affecting voter decisions about Harris
- Emotional responses to Harris's public appearances and statements

Ensure the analysis captures the nuanced reasons why voters are specifically undecided about Harris rather than general political uncertainty."""

            news_prompt = """You are an expert political analyst. Your task is to analyze news articles about voter uncertainty specifically regarding Kamala Harris.

For each set of articles, you must return a JSON object with this exact structure:
{
    "reasons": {
        "reason1": "percentage1",  # e.g. "approval_rating_fluctuation": "40%"
        "reason2": "percentage2"
    },
    "quotes": {
        "reason1": ["quote1", "quote2"],  # Expert quotes or polling data from articles
        "reason2": ["quote1", "quote2"]
    },
    "summary": "brief analysis of reported trends in voter uncertainty about Harris"
}

Focus specifically on:
- Polling data about Harris's approval ratings and voter perception
- Expert analysis of Harris's political positioning
- Demographic breakdowns of voter support/opposition
- Impact of Harris's policy initiatives and public statements
- Media coverage patterns and their effect on voter perception
- Comparisons with historical VP approval ratings
- Regional and demographic variations in voter uncertainty
- Quotes and specific reasons cited by voters are undecided

Prioritize factual reporting, polling data, expert analysis, and quotes from undecided voters."""

            # Select appropriate prompt based on source
            system_prompt = twitter_prompt if source == "twitter" else news_prompt

            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Here are {'tweets' if source == 'twitter' else 'news articles'} about voter uncertainty regarding Kamala Harris. Please analyze them and identify the specific reasons voters are undecided about her:\n\n{content}",
                    },
                ],
                temperature=0.5,
                max_tokens=1000,
            )

            # Get response content and log it for debugging
            response_content = response.choices[0].message.content.strip()
            print(f"OpenAI Response: {response_content}")

            if not response_content:
                print("Empty response from OpenAI")
                return

            # Remove any potential markdown code block formatting
            if response_content.startswith("```json"):
                response_content = response_content[7:-3]
            elif response_content.startswith("```"):
                response_content = response_content[3:-3]

            response_content = response_content.strip()
            analysis = json.loads(response_content)

            # Save weekly analysis
            WeeklyAnalysis.objects.update_or_create(
                week_start=week_start,
                week_end=week_end,
                source=source,
                defaults={
                    "total_posts_analyzed": posts.count(),
                    "reasons": analysis.get("reasons", ""),
                    "detailed_analysis": analysis.get("summary", ""),
                    "supporting_evidence": analysis.get("quotes", ""),
                },
            )

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Response content: {response_content}")
            raise
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            print(
                f"Response content: {response_content if 'response_content' in locals() else 'No response'}"
            )
            raise

    def get_weekly_trends(self, num_weeks=10, source="all"):
        """Get trends over multiple weeks for specified source"""
        query = WeeklyAnalysis.objects.order_by("-week_start")
        if source != "all":
            query = query.filter(source=source)
        return query[:num_weeks]
