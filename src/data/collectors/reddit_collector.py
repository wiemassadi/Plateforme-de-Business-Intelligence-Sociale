"""
REDDIT COLLECTOR - GÉNÉRATION DYNAMIQUE DE DONNÉES
===================================================

Génère des posts réalistes qui évoluent à chaque itération:
- Sentiments variables (positif/négatif)
- Événements simulés (crises, tendances)
- Métriques réalistes
"""

import logging
import random
from datetime import datetime, timedelta
from typing import List
from src.core.models.social_data import SocialPost, Platform, BusinessCategory


class DynamicRedditCollector:
    """Collecteur Reddit avec données évolutives"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.iteration = 0
        self.post_id = 0
        
        # Templates de posts par sentiment
        self.post_templates = {
            BusinessCategory.TECHNOLOGY: {
                'positive': [
                    "🚀 Just deployed our new AI system - 40% faster processing! Game changer for data science.",
                    "Python 3.12 is incredible! The performance improvements are real. Loving the new features.",
                    "Our startup just got Series A funding! $10M to scale our ML platform. Exciting times! 🎉",
                    "ChatGPT integration doubled our productivity. AI tools are transforming software development.",
                    "Cloud costs down 60% after optimization. AWS tricks that actually work for startups."
                ],
                'negative': [
                    "Latest Python update broke our entire codebase. Hours wasted fixing compatibility issues. 😤",
                    "AI hype is getting ridiculous. Most 'AI' products are just basic automation with fancy names.",
                    "Cloud services raising prices AGAIN. AWS/Azure becoming too expensive for small businesses.",
                    "Tech layoffs continuing. Even profitable companies cutting engineers. Industry feels broken.",
                    "Security breach exposed 100K user records. When will companies take cybersecurity seriously? 🔒"
                ]
            },
            BusinessCategory.FASHION: {
                'positive': [
                    "Sustainable fashion brands are finally mainstream! Patagonia's model is inspiring everyone. 🌿",
                    "This vintage jacket from ThredUp is amazing quality. Second-hand shopping FTW!",
                    "Fashion week was incredible! Designers embracing diversity and sustainability. Progress! ✨",
                    "Found the perfect eco-friendly sneakers. Stylish AND sustainable is possible!",
                    "Small independent designers are crushing it on Instagram. Supporting local fashion! 👗"
                ],
                'negative': [
                    "Fast fashion waste is destroying the planet. Shein/Zara need to be held accountable. 🌍",
                    "Ordered online, quality was terrible. Photos vs reality = complete scam. Requesting refund.",
                    "Luxury brands raising prices 30% with ZERO quality improvement. Pure greed.",
                    "Influencer promoting cheap knockoffs as 'affordable fashion'. Misleading followers for money. 👎",
                    "Return policy nightmare. Paid $50 shipping for a defective item. Customer service ignored me."
                ]
            },
            BusinessCategory.GAMING: {
                'positive': [
                    "New Elden Ring DLC is masterpiece level! FromSoftware never disappoints. GOTY material. 🎮",
                    "PS5 finally in stock at MSRP! Scalper era is over. Gaming is healing.",
                    "Indie game 'Hollow Knight Silksong' announced! Best news for gaming in years! 🔥",
                    "Xbox Game Pass value is insane. 300+ games for $15/month. PC gaming revolution.",
                    "Esports tournament hit 5M viewers! Gaming is mainstream entertainment now. 📈"
                ],
                'negative': [
                    "Another broken AAA launch. $70 for an unfinished game full of bugs. Refunding. 🐛",
                    "Microtransactions ruined this game. $20 for a skin? Gaming industry is pure greed now.",
                    "Servers down on release day AGAIN. How do billion-dollar companies fail basic infrastructure?",
                    "Battle pass FOMO tactics are predatory. Stop manipulating players psychologically. 😠",
                    "Game reviews were paid off. Actual gameplay is nothing like trailers. False advertising."
                ]
            },
            BusinessCategory.BUSINESS: {
                'positive': [
                    "Startup raised $50M Series B! Remote-first SaaS model working perfectly. 🚀",
                    "4-day work week trial = 20% productivity increase! Future of work is here.",
                    "Small business revenue up 200% after TikTok marketing. Social media works! 📊",
                    "Employee ownership model = happier team + better results. Capitalism done right.",
                    "Negotiated 50% pay raise by switching jobs. Know your worth in this market! 💰"
                ],
                'negative': [
                    "Tech startup laid off 40% of staff after raising $100M. VC money wasted on vanity metrics. 📉",
                    "Return to office mandate = immediate resignations. Companies don't learn. Remote works.",
                    "Middle managers adding zero value but making 2x engineer salaries. Corporate waste.",
                    "Startup burned through runway in 8 months. No business model, just vibes. Bubble 2.0. 💸",
                    "Toxic workplace culture. CEO gaslighting employees about 'mission'. Run away fast. 🚩"
                ]
            },
            BusinessCategory.ENTERTAINMENT: {
                'positive': [
                    "New Marvel series is actually GOOD! Finally quality content from Disney+. 🎬",
                    "Barbenheimer phenomenon showed cinema is alive! Record box office. Movies are back! 🍿",
                    "Spotify algorithm introduced me to 20 new artists. Music discovery working perfectly. 🎵",
                    "Netflix investing in anime = mainstream recognition. Streaming wars benefiting viewers.",
                    "Concert tickets at reasonable prices! Artist bypassing Ticketmaster. This is the way. 🎤"
                ],
                'negative': [
                    "Netflix cancelled another great show after 1 season. Stop doing this! 😤",
                    "Movie ticket + popcorn = $50. Cinema pricing is insane. Waiting for streaming.",
                    "Ticketmaster fees doubled the ticket price. Legal scalping. Concert industry is broken. 🎫",
                    "CGI looks worse than 10 years ago despite bigger budgets. Studios cutting corners.",
                    "Streaming service raising prices AGAIN while removing content. Piracy makes sense now. 🏴‍☠️"
                ]
            }
        }
    
    def collect_business_data(self) -> List[SocialPost]:
        
        """Génère 50 posts dynamiques qui évoluent"""
        self.iteration += 1
        posts = []
        
        # Simuler des événements spéciaux
        event_modifier = self._get_event_modifier()
        
        self.logger.info(f"📊 Reddit Collection - Iteration {self.iteration}")
        if event_modifier['name'] != 'normal':
            self.logger.info(f"🎯 Événement: {event_modifier['name']}")
        
        # Générer  posts par catégorie
        for category, templates in self.post_templates.items():
            # Ratio sentiment varie selon événements
            positive_ratio = 0.6 + event_modifier['sentiment_shift']
            postgenerated = random.randint(8, 12)
            for i in range(postgenerated):
                is_positive = random.random() < positive_ratio
                sentiment_type = 'positive' if is_positive else 'negative'
                
                # Choisir template aléatoire
                content = random.choice(templates[sentiment_type])
                
                # Métriques variables
                base_upvotes = random.randint(100, 5000)
                if event_modifier['viral_multiplier'] > 1:
                    base_upvotes = int(base_upvotes * event_modifier['viral_multiplier'])
                
                post = SocialPost(
                    id=f"reddit_{self.iteration}_{self.post_id}",
                    platform=Platform.REDDIT,
                    content=content,
                    author=f"u/redditor_{random.randint(1000, 9999)}",
                    author_followers=random.randint(5000, 50000),
                    created_at=datetime.now() - timedelta(minutes=random.randint(1, 30)),
                    url=f"https://reddit.com/r/{category.value}/comments/{self.post_id}",
                    metrics={
                        'upvotes': base_upvotes,
                        'comments': random.randint(10, 300),
                        'awards': random.randint(0, 10)
                    },
                    category=category,
                    metadata={
                        'subreddit': f"r/{category.value}",
                        'iteration': self.iteration,
                        'event': event_modifier['name']
                    }
                )
                
                posts.append(post)
                self.post_id += 1
        
        return posts
    def _get_event_modifier(self) -> dict:
            rand = random.random()
            
            # 10% événements très positifs
            if rand < 0.10:
                return {
                    'name': random.choice(['Viral Success', 'Product Launch', 'Award']),
                    'sentiment_shift': random.uniform(0.5, 0.8),  # ✅ +50% à +80% positifs
                    'viral_multiplier': random.uniform(5.0, 10.0)
                }
            
            # 15% événements positifs
            elif rand < 0.25:
                return {
                    'name': random.choice(['Partnership', 'Review', 'Update']),
                    'sentiment_shift': random.uniform(0.2, 0.4),  # ✅ +20% à +40% positifs
                    'viral_multiplier': random.uniform(2.0, 4.0)
                }
            
            # 10% événements très négatifs
            elif rand < 0.35:
                return {
                    'name': random.choice(['Data Breach', 'Scandal', 'Layoffs']),
                    'sentiment_shift': random.uniform(-0.8, -0.5),  # ✅ +50% à +80% négatifs
                    'viral_multiplier': random.uniform(6.0, 12.0)
                }
            
            # 15% événements négatifs
            elif rand < 0.50:
                return {
                    'name': random.choice(['Outage', 'Price Hike', 'Complaints']),
                    'sentiment_shift': random.uniform(-0.5, -0.3),  # ✅ +30% à +50% négatifs
                    'viral_multiplier': random.uniform(3.0, 6.0)
                }
            
            # 50% événements normaux
            else:
                return {
                    'name': 'normal',
                    'sentiment_shift': random.uniform(-0.15, 0.15),  # ✅ Légère variance
                    'viral_multiplier': 1.0
                }

if __name__ == "__main__":
    collector = DynamicRedditCollector()
    
    print("\n🧪 TEST - 3 itérations\n")
    for i in range(3):
        posts = collector.collect_business_data()
        
        positive = sum(1 for p in posts if any(word in p.content.lower() 
                       for word in ['amazing', 'incredible', 'best', 'love', '🚀', '🎉']))
        
        print(f"Iteration {i+1}: {len(posts)} posts, ~{positive} positifs")