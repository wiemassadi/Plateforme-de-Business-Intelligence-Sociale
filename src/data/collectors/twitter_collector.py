"""
TWITTER COLLECTOR - SIMULATION TEMPS RÉEL
==========================================
"""

import logging
import random
from datetime import datetime, timedelta
from typing import List
from src.core.models.social_data import SocialPost, Platform, BusinessCategory


class DynamicTwitterCollector:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.iteration = 0
        self.post_id = 0
        self.trending_hashtags = []
        
        self.tweet_templates = {
            BusinessCategory.TECHNOLOGY: {
                'positive': [
                    "AI coding assistants are incredible! Just built a full app in 2 hours with Claude/GPT-4. 🚀 #AI #Coding",
                    "Python performance improvements in 3.12 are REAL. Benchmarks showing 25% speedup! 🐍 #Python",
                    "Open source is winning. Companies choosing Linux/PostgreSQL over proprietary. #OpenSource",
                    "Tech salaries up 30% YoY. Skills shortage means developers have leverage! 💰 #TechJobs",
                    "Cloud native architecture saved us $500K/year. Kubernetes complexity worth it! ☁️ #DevOps"
                ],
                'negative': [
                    "Another AI tool overpromising and underdelivering. Stop the hype cycle! 🛑 #AIHype",
                    "Big Tech layoffs continuing despite record profits. Greed over people. 😠 #TechLayoffs",
                    "Privacy nightmare: app was secretly selling user data for years. Delete now! 🔐 #Privacy",
                    "npm install = 500MB of dependencies for Hello World. JS ecosystem is broken. 📦 #JavaScript",
                    "AWS bill increased 3x overnight due to 'pricing changes'. Lock-in trap! 💸 #Cloud"
                ]
            },
            BusinessCategory.FASHION: {
                'positive': [
                    "Thrifted this vintage leather jacket for $30. Sustainable fashion is the future! ♻️ #SustainableFashion",
                    "Small designers on Etsy > mass production. Quality and ethics matter! 🌿 #SlowFashion",
                    "Fashion week finally featuring plus-size models. Representation matters! ✨ #BodyPositivity",
                    "Capsule wardrobe changed my life. 30 pieces, infinite combinations. Less is more! 👗 #MinimalistFashion",
                    "Biodegradable sneakers that actually look good! Innovation in sustainable materials 🌱 #EcoFashion"
                ],
                'negative': [
                    "Fast fashion brands greenwashing while producing 100M garments/year. Stop the lies! 🌍 #Greenwashing",
                    "Influencer promoting $5 clothes made in sweatshops. Unethical 'haul culture' needs to end. 😡",
                    "$200 designer t-shirt = same quality as $20 one. Paying for logos, not quality. 💰 #Overpriced",
                    "Online order arrived: nothing like photos, terrible quality, non-refundable. SCAM! 👎 #OnlineShopping",
                    "Luxury brands using child labor while charging $1000+ for bags. Disgusting. 🚨 #EthicalFashion"
                ]
            },
            BusinessCategory.GAMING: {
                'positive': [
                    "Baldur's Gate 3 is masterpiece. 10/10. Proves AAA can still deliver quality! 🎮 #BG3 #Gaming",
                    "Indie games > AAA garbage. Hollow Knight, Hades, Celeste are art. 🎨 #IndieGames",
                    "Xbox Game Pass = best value in gaming. 300+ games for price of 1 AAA. 🎯 #GamePass",
                    "Esports athlete earning $2M/year. Gaming is legitimate career now! 🏆 #Esports",
                    "VR gaming finally hit mainstream. Quest 3 is incredible experience! 🥽 #VRGaming"
                ],
                'negative': [
                    "Paid $70 for broken game. Day 1 patch = 50GB. Released unfinished! 🐛 #Gaming #Broken",
                    "$20 for cosmetic skin. Microtransactions ruining gaming. Vote with your wallet! 💸 #Gaming",
                    "Servers down 6 hours on launch day. Billion dollar company can't handle traffic? 🔴 #ServerDown",
                    "Pay-to-win mechanics in $60 game. EA/Activision greed destroying franchises. 😠 #Gaming",
                    "Review bombing deserved. Devs lied about features, game is nothing like trailer. 👎 #FalseAdvertising"
                ]
            },
            BusinessCategory.BUSINESS: {
                'positive': [
                    "Startup hit $10M ARR in 18 months! SaaS model + product-led growth = 🚀 #Startup #SaaS",
                    "Remote work = 40% cost savings + happier employees. Office leases are dead! 🏠 #RemoteWork",
                    "Small business got viral on TikTok, sales up 500%. Social media marketing works! 📱 #SmallBusiness",
                    "Employee stock options made me $500K. Equity compensation changing lives! 💰 #Startup #Equity",
                    "4-day work week: productivity UP, burnout DOWN. Future of work! ⏰ #4DayWorkWeek"
                ],
                'negative': [
                    "VC-backed startup burned $100M with no revenue. Bubble 2.0 popping! 📉 #StartupBubble",
                    "Toxic CEO fired entire team via Zoom on Friday. Corporate psychopaths! 😡 #ToxicWorkplace",
                    "Return-to-office mandate = mass exodus. Companies still don't get it. 🚪 #RTO #RemoteWork",
                    "Startup promised equity then diluted shares 10:1. Founders got rich, employees got nothing. 💸 #StartupScam",
                    "Unpaid internships at profitable companies. Legal slavery in 2024. Shameful! 🚨 #Exploitation"
                ]
            },
            BusinessCategory.ENTERTAINMENT: {
                'positive': [
                    "Oppenheimer is cinematic perfection. Nolan's best work. See it in IMAX! 🎬 #Oppenheimer",
                    "Indie film won Cannes! Original storytelling beating Marvel formula! 🏆 #IndieFilm",
                    "Spotify Wrapped = perfect algorithm. Discovered 50 new artists this year! 🎵 #SpotifyWrapped",
                    "The Bear Season 2 is TV perfection. Best show on streaming! 📺 #TheBear #TV",
                    "Concert tickets under $50! Artist using blockchain to fight scalpers. This is the future! 🎤 #Concerts"
                ],
                'negative': [
                    "Netflix cancelled 10 shows this month including my favorite. Stop doing this! 😡 #SaveOurShows",
                    "Streaming services now cost more than cable. We've come full circle. 💸 #Streaming #CordCutting",
                    "Ticketmaster 'dynamic pricing' = $400 for concert ticket. Legal scalping! 🎫 #TicketmasterSucks",
                    "CGI in $200M movie looks worse than 2010. Studios cutting corners while charging more. 🎬 #VFX",
                    "Another unnecessary remake/reboot. Hollywood has zero original ideas! 🔄 #Hollywood"
                ]
            }
        }
    
    def collect_business_trends(self) -> List[SocialPost]:
        """Collecte 50 tweets avec tendances évolutives"""
        self.iteration += 1
        posts = []
        
        event = self._get_event_type()
        
        self.logger.info(f"🐦 Twitter Collection - Iteration {self.iteration}")
        if event['name'] != 'normal':
            self.logger.info(f"🔥 Event: {event['name']}")
        
        #  tweets par catégorie
        for category, templates in self.tweet_templates.items():
            base_ratio = 0.3
            positive_ratio = max(0.0, min(1.0, base_ratio + event['sentiment_shift']))
            
            posts_per_category = random.randint(8, 12)
            for i in range(posts_per_category):
                is_positive = random.random() < positive_ratio
                content = random.choice(templates['positive' if is_positive else 'negative'])
                
                # Métriques réalistes Twitter
                likes = random.randint(50, 5000)
                if event['viral']:
                    likes *= random.randint(2, 10)
                
                post = SocialPost(
                    id=f"twitter_{self.iteration}_{self.post_id}",
                    platform=Platform.TWITTER,
                    content=content,
                    author=f"@user{random.randint(1000, 9999)}",
                    author_followers=random.randint(1000, 100000),
                    created_at=datetime.now() - timedelta(minutes=random.randint(1, 30)),
                    url=f"https://twitter.com/status/{self.post_id}",
                    metrics={
                        'likes': likes,
                        'retweets': likes // random.randint(5, 10),
                        'replies': likes // random.randint(10, 20),
                        'quotes': likes // random.randint(20, 50)
                    },
                    category=category,
                    metadata={
                        'iteration': self.iteration,
                        'event': event['name'],
                        
                    }
                )
                
                posts.append(post)
                self.post_id += 1
        
        return posts
    
  
    def _get_event_type(self) -> dict:
        rand = random.random()
    
        # 10% événements très positifs
        if rand < 0.10:
            return {
                'name': random.choice(['Viral Success', 'Product Launch', 'Award']),
                'sentiment_shift': random.uniform(0.5, 0.8), 
                'viral_multiplier': random.uniform(5.0, 10.0),
                'viral': True
            }
        
        # 15% événements positifs
        elif rand < 0.25:
            return {
                'name': random.choice(['Partnership', 'Review', 'Update']),
                'sentiment_shift': random.uniform(0.2, 0.4), 
                'viral_multiplier': random.uniform(2.0, 4.0),
                'viral': True
            }
        
        # 10% événements très négatifs
        elif rand < 0.35:
            return {
                'name': random.choice(['Data Breach', 'Scandal', 'Layoffs']),
                'sentiment_shift': random.uniform(-0.8, -0.5),  
                'viral_multiplier': random.uniform(6.0, 12.0),
                'viral': True
            }
        
        # 15% événements négatifs
        elif rand < 0.50:
            return {
                'name': random.choice(['Outage', 'Price Hike', 'Complaints']),
                'sentiment_shift': random.uniform(-0.5, -0.3),  
                'viral_multiplier': random.uniform(3.0, 6.0),
                'viral': True
            }
        
        # 50% événements normaux
        else:
            return {
                'name': 'normal',
                'sentiment_shift': random.uniform(-0.15, 0.15),  
                'viral_multiplier': 1.0,
                'viral': False
            }