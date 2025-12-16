"""
TIKTOK COLLECTOR - VERSION AMÉLIORÉE
====================================
Ajout de posts positifs/négatifs + événements dynamiques
"""

import logging
import random
from datetime import datetime, timedelta
from typing import List
from src.core.models.social_data import SocialPost, Platform, BusinessCategory


class DynamicTikTokCollector:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.iteration = 0
        self.post_id = 0
        self.trending_hashtags = []
        
        # NOUVEAU: Templates avec sentiments positifs/négatifs par catégorie
        self.tiktok_templates = {
            BusinessCategory.TECHNOLOGY: {
                'positive': [
                    "POV: You're a software engineer in 2024 💻 Living the dream! Remote work + high salary 🚀 #TechTok #Coding #DeveloperLife",
                    "AI vs Human challenge! 🤖 AI lost, humans still superior! 💪 #AIChallenge #Tech #HumanWins",
                    "Day in life of a developer ☕💻 Best job ever! Solving problems all day 🧠 #DITL #Programming #TechCareer",
                    "Just got hired at FAANG! 🎉 $200K starting salary at 22yo 💰 Dream come true! #TechJobs #Career #Success",
                    "Coding bootcamp changed my life! 🚀 From $30K to $120K in 6 months! #LearnToCode #CareerChange #TechSuccess",
                    "This AI tool saves me 10 hours per week! 🤖⚡ Game changer for developers! #AITools #Productivity #TechTok",
                    "Built my first startup MVP in 48h! 💻🔥 No-code tools are amazing! #StartupLife #NoCode #Tech"
                ],
                'negative': [
                    "POV: You spent 8 hours debugging... turns out it was a semicolon 😤 #Coding #DeveloperLife #Frustration",
                    "AI took my job... seriously. 🤖💔 Tech industry is brutal right now #AIChallenge #Unemployed #TechLayoffs",
                    "Day in life of a developer: burnout edition 😓 60h weeks for mediocre pay #DITL #TechBurnout #ToxicWorkplace",
                    "Tech interview was 9 rounds for entry level position 🤯 This industry is broken! #TechInterview #JobSearch #Nightmare",
                    "Coding bootcamp scam exposed! 💸😠 $15K wasted, no job, outdated curriculum #Bootcamp #Scam #RegretIt",
                    "This AI tool deleted my entire codebase 💀 3 months of work GONE! #AIFail #TechNightmare #DataLoss",
                    "Startup failed after 2 years... $100K in debt 😭 Don't quit your day job! #StartupFail #Entrepreneur #Reality"
                ]
            },
            BusinessCategory.FASHION: {
                'positive': [
                    "Styling the same outfit 5 ways! ✨ Versatility queen 👑 Save money, look amazing! #FashionHack #Style #OOTD",
                    "Thrift flip transformation! 🔄👗 $5 dress → $500 designer look! Sustainable fashion wins 🌿 #ThriftFlip #DIY #Sustainable",
                    "Get ready with me! 💄✨ Affordable makeup that WORKS! All under $50! #GRWM #Fashion #MakeupTutorial",
                    "Found the perfect jeans! 👖😍 Finally a brand that fits ALL body types! #FashionFind #BodyPositive #Inclusive",
                    "DIY fashion hack went viral! 🔥 1M views in 24h! Thanks for the love! ❤️ #FashionHack #Viral #DIY",
                    "Sustainable fashion haul! 🌱👗 These eco-brands are GORGEOUS and affordable! #Sustainable #Fashion #EcoFriendly",
                    "Fashion week behind the scenes! ✨ Dreams really do come true! 🤩 #FashionWeek #Model #DreamJob"
                ],
                'negative': [
                    "Styling fail... 😅 What was I thinking?! Fashion mistakes we all make 🤦‍♀️ #FashionFail #Oops #Style",
                    "Thrift flip DISASTER! 🔄💔 Ruined a $30 jacket trying to be creative 😭 #ThriftFlip #DIYFail #Regret",
                    "Get ready with me: reality edition 😓 Makeup didn't last 2 hours... waste of $80! #GRWM #MakeupFail #Disappointed",
                    "These jeans are FALSE ADVERTISING! 👖😤 Nothing like the photos, returning ASAP! #FashionFail #OnlineShopping #Scam",
                    "Fast fashion haul regret... 🛍️😞 Everything fell apart after 1 wash. NEVER AGAIN! #FastFashion #Poor Quality #Waste",
                    "Sustainable fashion is TOO EXPENSIVE! 💸😠 $200 for a t-shirt?! Not accessible! #Sustainable #Expensive #Frustrated",
                    "Fashion industry toxicity exposed! 😡 Size discrimination is REAL and disgusting! #Fashion #SizeInclusive #Problem"
                ]
            },
            BusinessCategory.GAMING: {
                'positive': [
                    "Insane gaming moment! 🎮🔥 1v5 clutch for the WIN! Best play of my life! #Gaming #Clutch #ProGamer",
                    "Building the ultimate setup! 💰✨ Saved for 2 years, finally complete! Worth every penny! #GamingSetup #PC #Battlestation",
                    "Noob vs Pro comparison! 😂🎮 We all started somewhere! Keep practicing! 💪 #Gaming #Funny #GamingTips",
                    "Just hit Challenger rank! 🏆🎮 3000 hours of grinding paid off! Dreams come true! #Gaming #Esports #Achievement",
                    "Gaming with the squad! 👾😂 Best nights ever! This is what gaming is about! ❤️ #Gaming #Squad #Friendship",
                    "Charity gaming stream raised $10K! 🎮❤️ Gaming community is the BEST! #CharityStream #Gaming #Community",
                    "Got sponsored by my favorite brand! 🎮🔥 Gaming dreams coming true! Thank you all! 🙏 #Sponsored #Gaming #Success"
                ],
                'negative': [
                    "Insane gaming rage moment! 🎮😡 Lost to hackers AGAIN! Game is unplayable! #Gaming #Hackers #Rage",
                    "Building the ultimate setup... and my GPU died 💀💸 $800 gone, no warranty #GamingSetup #PC #Nightmare",
                    "Noob vs Pro comparison: I'm still noob after 1000 hours 😭 Talent vs hard work... talent wins #Gaming #Depressing #Reality",
                    "$70 for a BROKEN game?! 🐛💸 Day 1 patch is 80GB! This is theft! #Gaming #BrokenGame #Refund",
                    "Gaming addiction ruined my life 😔 Failed school, lost friends... be careful #Gaming #Addiction #MentalHealth",
                    "Toxic gaming community strikes again 😡 Harassment and hate in every match! #Gaming #Toxic #Problem",
                    "Pay-to-win destroyed this game 💸🎮 $500 spent and still losing to credit cards! #Gaming #P2W #Greed"
                ]
            },
            # Ajout de 2 catégories manquantes pour avoir 60 posts
            BusinessCategory.BUSINESS: {
                'positive': [
                    "From 0 to $10K/month in 6 months! 📈💰 Side hustle SUCCESS story! #Entrepreneur #Business #Success",
                    "Quit my 9-5 to start my business! 🚀 Best decision ever! Living the dream! #Entrepreneur #Freedom #Business",
                    "Small business owner life! 💼✨ Hard work but SO rewarding! #SmallBusiness #Entrepreneur #BossLife"
                ],
                'negative': [
                    "Lost everything in my startup... 💔😭 $50K debt, back to 9-5 #Entrepreneur #StartupFail #Reality",
                    "Quit my job for business... biggest mistake 😓 Stable income > uncertainty #Business #Regret #JobSearch",
                    "Small business owner reality: burnout 😤💼 80h weeks, barely breaking even #SmallBusiness #Burnout #Struggle"
                ]
            },
            BusinessCategory.ENTERTAINMENT: {
                'positive': [
                    "Behind the scenes of my music video! 🎬✨ Creative process is magical! #Entertainment #Music #BTS",
                    "Concert experience was INCREDIBLE! 🎤🔥 Best night of my life! Worth every penny! #Concert #Music #Live",
                    "Movie review: This film is a MASTERPIECE! 🎬😍 Go watch it NOW! #Movie #Review #MustWatch"
                ],
                'negative': [
                    "Behind the scenes reality: chaos 🎬😅 Nothing goes as planned in entertainment! #Entertainment #BTS #Reality",
                    "Concert was TERRIBLE! 🎤😡 $300 ticket for 45min performance?! Scam! #Concert #Disappointed #Ripoff",
                    "Movie was trash 🎬🗑️ 2 hours wasted! Don't believe the hype! #Movie #Review #Terrible"
                ]
            }
        }
    
    def collect_trending_content(self) -> List[SocialPost]:
        """Collecte posts TikTok avec sentiments variés"""
        self.iteration += 1
        posts = []
        
        # Obtenir événement actuel pour variance sentiments
        event = self._get_event_modifier()
        
        self.logger.info(f"📱 TikTok Collection - Iteration {self.iteration}")
        if event['name'] != 'normal':
            self.logger.info(f"🎯 TikTok Event: {event['name']} "
                           f"(sentiment: {event['sentiment_shift']:+.2f})")
        
       
        
        # Générer posts pour chaque catégorie
        for category, templates in self.tiktok_templates.items():
            # Calculer nombre de posts par catégorie 
            posts_per_category = random.randint(10, 15)
            # Calculer ratio positif/négatif selon événement
            base_ratio = 0.5
            positive_ratio = max(0.0, min(1.0, base_ratio + event['sentiment_shift']))
            
            for i in range(posts_per_category):
                # Choisir sentiment selon ratio
                is_positive = random.random() < positive_ratio
                sentiment_type = 'positive' if is_positive else 'negative'
                
                # Choisir template aléatoire
                content = random.choice(templates[sentiment_type])
                
                # Ajouter hashtags trending si disponibles
                if self.trending_hashtags and random.random() > 0.5:
                    content += f" {random.choice(self.trending_hashtags)}"
                
                # Métriques réalistes TikTok (basées sur vues)
                base_views = random.randint(10000, 1000000)
                
                # Multiplicateur si événement viral
                if event.get('is_viral', False):
                    base_views = int(base_views * event['viral_multiplier'])
                
                # TikTok: likes sont ~10% des vues
                likes = int(base_views * random.uniform(0.05, 0.15))
                comments = int(base_views * random.uniform(0.005, 0.015))
                shares = int(base_views * random.uniform(0.002, 0.008))
                
                post = SocialPost(
                    id=f"tiktok_{self.iteration}_{self.post_id}",
                    platform=Platform.TIKTOK,
                    content=content,
                    author=f"@tiktok{random.randint(100, 999)}",
                    author_followers=random.randint(10000, 1000000),
                    created_at=datetime.now() - timedelta(minutes=random.randint(1, 30)),
                    url=f"https://tiktok.com/@user/video/{self.post_id}",
                    metrics={
                        'likes': likes,
                        'comments': comments,
                        'shares': shares,
                        'views': base_views
                    },
                    category=category,
                    metadata={
                        'iteration': self.iteration,
                        'event': event['name']
                    
                    }
                )
                posts.append(post)
                self.post_id += 1
        
        return posts
    
    def _get_event_modifier(self) -> dict:
        """
        Génère événements avec forte variance pour sentiments dynamiques
        Identique à la logique des autres collecteurs
        """
        rand = random.random()
        
        # 10% événements très positifs
        if rand < 0.10:
            return {
                'name': random.choice(['Viral Video', 'Challenge Success', 'Creator Award']),
                'sentiment_shift': random.uniform(0.5, 0.8),
                'viral_multiplier': random.uniform(5.0, 10.0),
                'is_viral': True
            }
        
        # 15% événements positifs
        elif rand < 0.25:
            return {
                'name': random.choice(['Trend Starting', 'Positive Collab', 'Milestone']),
                'sentiment_shift': random.uniform(0.2, 0.4),
                'viral_multiplier': random.uniform(2.0, 4.0),
                'is_viral': False
            }
        
        # 10% événements très négatifs
        elif rand < 0.35:
            return {
                'name': random.choice(['Platform Ban', 'Scandal Exposed', 'Lawsuit']),
                'sentiment_shift': random.uniform(-0.8, -0.5),
                'viral_multiplier': random.uniform(6.0, 12.0),
                'is_viral': True
            }
        
        # 15% événements négatifs
        elif rand < 0.50:
            return {
                'name': random.choice(['Algorithm Change', 'Drama', 'Criticism']),
                'sentiment_shift': random.uniform(-0.5, -0.3),
                'viral_multiplier': random.uniform(3.0, 6.0),
                'is_viral': True
            }
        
        # 50% événements normaux
        else:
            return {
                'name': 'normal',
                'sentiment_shift': random.uniform(-0.15, 0.15),
                'viral_multiplier': 1.0,
                'is_viral': False
            }
    

# ============================================
# TEST UNITAIRE
# ============================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print("🧪 TEST TIKTOK COLLECTOR - VERSION AMÉLIORÉE")
    print("="*70)
    
    collector = DynamicTikTokCollector()
    
    # Tester 5 cycles
    for cycle in range(1, 6):
        print(f"\n{'='*70}")
        print(f"📊 CYCLE {cycle}/5")
        print("="*70)
        
        posts = collector.collect_trending_content()
        
        # Compter sentiments (approximation basée sur mots-clés)
        positive_keywords = ['amazing', 'best', 'love', 'dream', 'success', 'win', 'incredible', '🎉', '🔥', '✨', '😍', '💪', '🚀']
        negative_keywords = ['fail', 'disaster', 'broke', 'scam', 'toxic', 'rage', 'lost', 'nightmare', '😭', '😡', '😤', '💔', '😓']
        
        positive = sum(1 for p in posts if any(w in p.content.lower() for w in positive_keywords))
        negative = sum(1 for p in posts if any(w in p.content.lower() for w in negative_keywords))
        neutral = len(posts) - positive - negative
        
        print(f"\n✅ {len(posts)} posts TikTok collectés")
        print(f"\n📊 DISTRIBUTION SENTIMENTS:")
        print(f"  🟢 Positifs: {positive:2d} ({positive/len(posts)*100:5.1f}%)")
        print(f"  🔴 Négatifs: {negative:2d} ({negative/len(posts)*100:5.1f}%)")
        print(f"  ⚪ Neutres:  {neutral:2d} ({neutral/len(posts)*100:5.1f}%)")
        
        # Distribution par catégorie
        from collections import Counter
        categories = Counter(p.category.value for p in posts)
        print(f"\n🏷️  DISTRIBUTION CATÉGORIES:")
        for cat, count in categories.items():
            print(f"  • {cat:15} → {count:2d} posts")
        
        # Exemples de posts
        print(f"\n📝 EXEMPLES POSTS:")
        for i, post in enumerate(posts[:3]):
            print(f"\n{i+1}. [{post.category.value.upper()}]")
            print(f"   Content: {post.content[:100]}...")
            print(f"   Views: {post.metrics['views']:,} | Likes: {post.metrics['likes']:,}")
        
        # Pause entre cycles
        if cycle < 5:
            import time
            time.sleep(1)
    
    print("\n" + "="*70)
    print("✅ TEST TERMINÉ - TikTok Collector fonctionne avec variance!")
    print("="*70)