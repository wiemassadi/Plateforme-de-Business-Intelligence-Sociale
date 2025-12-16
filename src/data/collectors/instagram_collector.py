"""
INSTAGRAM COLLECTOR - SIMULATION TEMPS RÉEL AVANCÉE
====================================================
Structure identique à Twitter Collector avec:
- Tweets adaptés pour Instagram (style visuel + captions)
- Tendances spécifiques Instagram (Reels, Stories, etc.)
- Métriques réalistes Instagram
- Événements viraux spécifiques
- Templates par catégorie business
"""

import logging
import random
from datetime import datetime, timedelta
from typing import List
from src.core.models.social_data import SocialPost, Platform, BusinessCategory


class DynamicInstagramCollector:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.iteration = 0
        self.post_id = 0
        self.trending_topics = []
        
        # Captions Instagram par catégorie avec style IG spécifique (emojis, hashtags)
        self.instagram_captions = {
            BusinessCategory.TECHNOLOGY: {
                'positive': [
                    "Tech office tour 🏢✨ My minimalist workspace setup! Productivity increased 300% 📈 #TechSetup #MinimalistWorkspace #ProductivityHacks",
                    "Just unboxed the new M3 MacBook Pro 🎁🔥 This thing is a BEAST! Editing 8K video like butter 🎬 #Apple #Unboxing #TechReview",
                    "Our startup hit 100K users 🚀✨ 2 years of hard work paying off! So grateful for this team 💪 #StartupLife #TechStartup #Milestone",
                    "AI generated this entire website in 30 seconds 🤯 The future is WILD! What should I build next? 👇 #AIGenerated #WebDev #FutureTech",
                    "Remote work setup complete 🌴💻 Working from Bali this month! Digital nomad life is the dream ✈️ #DigitalNomad #RemoteWork #WorkFromAnywhere"
                ],
                'negative': [
                    "$3000 laptop and it's already having display issues 😤 Apple quality control is declining! #Apple #TechFail #Disappointed",
                    "Another 'revolutionary' tech product that's just a rebranded Chinese gadget 🥱 Stop the hype! #TechHype #Overpriced #ScamAlert",
                    "Data breach exposed 2M users' personal info 🚨 When will companies take security seriously? #DataBreach #Privacy #TechFail",
                    "SaaS company increased prices 200% overnight with no warning 💸 Loyal customers feeling betrayed #SaaS #PriceHike #CustomerBetrayal",
                    "This smart home device spies on you 24/7 🎤 Found it sending audio to China. Privacy nightmare! #SmartHome #Privacy #SecurityRisk"
                ]
            },
            BusinessCategory.FASHION: {
                'positive': [
                    "Thrift haul treasure hunt 🛍️✨ Found this vintage leather jacket for only $25! Sustainable fashion wins 🌿 #ThriftHaul #VintageFashion #SustainableStyle",
                    "Behind the scenes at fashion week! 📸✨ The energy is ELECTRIC! So honored to be here 🤩 #FashionWeek #Backstage #DreamComeTrue",
                    "Capsule wardrobe 30-day challenge ✅ 30 pieces, unlimited outfits! Minimalism changed my life 🙌 #CapsuleWardrobe #MinimalistFashion #StyleChallenge",
                    "Local designer spotlight 🌟 Supporting small businesses! This handmade dress is art 🎨 #SupportSmallBusiness #LocalDesigner #HandmadeFashion",
                    "Before & After: Clothing restoration magic! ✨ This jacket was headed to landfill, now it's my favorite piece ♻️ #ClothingRestoration #Upcycle #SustainableFashion"
                ],
                'negative': [
                    "Fast fashion haul gone wrong 😡 All 10 items arrived with defects or holes. Quality is nonexistent! #FastFashion #PoorQuality #ShoppingFail",
                    "$500 'designer' dress vs $50 dupe = identical quality 🤥 Paying for the label, not the product! #DesignerFashion #Overpriced #FashionScam",
                    "Shein haul regret 😞 Clothes disintegrated after 2 washes. Never again! #Shein #FastFashion #RegretPurchase",
                    "Influencer promoting $1000 bag made by child laborers 🚨 Unethical fashion needs to stop! #EthicalFashion #ChildLabor #FashionExposed",
                    "Sustainable brand caught using polyester labeled as organic cotton 🌱 Greenwashing at its finest! #Greenwashing #SustainableFashion #Exposed"
                ]
            },
            BusinessCategory.GAMING: {
                'positive': [
                    "Gaming room makeover complete! 🎮✨ RGB heaven meets ergonomic perfection. 12-hour sessions, no problem! 😎 #GamingSetup #Battlestation #GamingRoom",
                    "Just hit Diamond rank! 🏆🎮 After 300 hours of grinding, this feels AMAZING! Never give up on your goals 💪 #Gaming #RankUp #Achievement",
                    "Esports tournament backstage! 🎮✨ The energy is UNREAL! Competing with legends tonight ⚡ #Esports #GamingTournament #ProGamer",
                    "Charity gaming stream raised $50K for kids! 🎮❤️ Gaming community is the BEST! So proud of everyone who donated 🙏 #CharityStream #GamingForGood #Community",
                    "VR gaming party! 🥽🎉 Everyone tried Beat Saber for the first time - pure joy and laughter! VR brings people together! #VRGaming #BeatSaber #GamingParty"
                ],
                'negative': [
                    "$70 game released broken 🐛 Day one patch is 100GB? Unacceptable! #BrokenGame #ReleaseFail #GamingIndustry",
                    "Gaming chair review: $500 for back pain 😫 Marketing vs reality! Save your money! #GamingChair #ProductReview #WasteOfMoney",
                    "Server issues for 48 hours straight 🔴 Multiplayer game unplayable. Refund requested! #ServerIssues #GameDown #Refund",
                    "Loot boxes = gambling for kids 🎰 When will regulations catch up? #LootBoxes #Gambling #GamingRegulation",
                    "Console exclusivity is ANTI-CONSUMER 🚫 Paying $500 to play one game? This needs to stop! #ConsoleExclusivity #AntiConsumer #Gaming"
                ]
            },
            BusinessCategory.BUSINESS: {
                'positive': [
                    "From side hustle to 7-figure business! 📈✨ 3 years ago I started with $100, today we hit $1M revenue. BELIEVE IN YOURSELF! 💪 #Entrepreneur #SuccessStory #BusinessGrowth",
                    "Team retreat in the mountains! 🏔️✨ Nothing like nature to spark creativity and strengthen bonds. Best team EVER! ❤️ #TeamBuilding #CompanyRetreat #WorkCulture",
                    "Office makeover reveal! 🏢💫 Went from dull cubicles to creative collaborative space. Productivity skyrocketed! 📈 #OfficeDesign #WorkEnvironment #Productivity",
                    "Just signed our 100th client! 🎉📝 Started with cold emails, now we're industry leaders. Persistence pays off! #BusinessMilestone #ClientSuccess #Growth",
                    "Launched our sustainability initiative 🌱♻️ Company going carbon neutral by 2025! Business can be a force for good! #SustainableBusiness #CorporateResponsibility #EcoFriendly"
                ],
                'negative': [
                    "Company layoffs announced via email 😡 No warning, no severance. Treating people like numbers! #Layoffs #ToxicWorkplace #CorporateGreed",
                    "Return to office mandate despite 2 years of successful remote work 🏢📉 Productivity dropped 40%. Management stuck in the past! #RTO #RemoteWork #ManagementFail",
                    "CEO bought $10M yacht while cutting employee benefits 🛥️💰 Priorities completely wrong! #CorporateGreed #IncomeInequality #BadLeadership",
                    "Startup promised equity then diluted shares 100:1 📉 Founders millionaires, employees got nothing. SCAM! #StartupScam #Equity #EmployeeBetrayal",
                    "Company culture is TOXIC 😷 Micromanagement, burnout, high turnover. Looking for new opportunities! #ToxicWorkplace #CompanyCulture #JobSearch"
                ]
            },
            BusinessCategory.ENTERTAINMENT: {
                'positive': [
                    "Concert backstage access! 🎤✨ Met my idol after 10 years of fandom. Cried happy tears! 😭❤️ #Concert #Backstage #DreamComeTrue",
                    "Film festival premiere! 🎬✨ Our indie film getting standing ovation! Years of hard work paying off! 👏 #FilmFestival #IndieFilm #Premiere",
                    "Recording studio session 🎧✨ Working on new music with amazing artists! Creative energy is flowing! 🎶 #RecordingStudio #MusicProduction #ArtistLife",
                    "Broadway opening night! 🎭✨ The magic of live theater is unmatched! So proud of this cast and crew! #Broadway #Theater #OpeningNight",
                    "Comedy club sold out! 🎤😂 Nothing like making 500 people laugh in one night. Best feeling ever! #StandupComedy #SoldOutShow #ComedianLife"
                ],
                'negative': [
                    "Paid $500 for concert tickets, obstructed view 😡 Ticketmaster should show view before purchase! #Ticketmaster #Concert #Scammed",
                    "Movie spoilers EVERYWHERE 24 hours after release 🚫 Can't enjoy anything without social media ruining it! #Spoilers #Movie #SocialMedia",
                    "$15 popcorn and $8 water at cinema 🍿💸 Robbery in broad daylight! #MovieTheater #Overpriced #Cinema",
                    "Streaming service removed my favorite show with NO WARNING 📺💔 Why do we pay for these services? #Streaming #ContentRemoval #Disappointed",
                    "Influencer festival: $500 ticket for basic food trucks and photo ops 📸💰 Complete waste of money! #InfluencerEvent #WasteOfMoney #ScamFestival"
                ]
            }
        }
    
    def collect_business_posts(self) -> List[SocialPost]:
        """Collecte 50 posts Instagram avec tendances évolutives"""
        self.iteration += 1
        posts = []
        
      
        # Type d'événement Instagram (Reels viral, Stories trend, etc.)
        event = self._get_instagram_event_type()
        
        self.logger.info(f"📸 Instagram Collection - Iteration {self.iteration}")
        if event['name'] != 'normal':
            self.logger.info(f"🔥 Instagram Event: {event['name']}")
        
        #  posts par catégorie business
        for category, templates in self.instagram_captions.items():
            base_ratio = 0.5
            positive_ratio = max(0.0, min(1.0, base_ratio + event['sentiment_shift']))
            posts_per_category = random.randint(11, 17)
            for i in range(posts_per_category):
                is_positive = random.random() < positive_ratio
                content = random.choice(templates['positive' if is_positive else 'negative'])
                
                # Métriques réalistes Instagram (plus de likes, moins de comments que Twitter)
                base_likes = random.randint(1000, 50000)  # Instagram a généralement plus de likes
                if event['viral']:
                    base_likes *= random.randint(3, 15)  # Reels viraux peuvent exploser
                
                # Type de post Instagram (Feed, Reels, Stories)
                post_type = random.choice(['feed', 'reels', 'carousel'])
                
                post = SocialPost(
                    id=f"instagram_{self.iteration}_{self.post_id}",
                    platform=Platform.INSTAGRAM,
                    content=content,
                    author=f"@{random.choice(['fashion', 'tech', 'lifestyle', 'travel'])}{random.randint(100, 9999)}",
                    author_followers=random.randint(10000, 1000000),  # Instagram a généralement plus de followers
                    created_at=datetime.now() - timedelta(minutes=random.randint(1, 30)),
                    url=f"https://instagram.com/p/IG_{self.post_id}",
                    metrics={
                        'likes': base_likes,
                        'comments': base_likes // random.randint(50, 200),  # Ratio comments/likes plus bas sur IG
                        'saves': base_likes // random.randint(10, 30),      # Unique à Instagram
                        'shares': base_likes // random.randint(100, 500),   # Shares (DM)
                        'views': base_likes * random.randint(3, 10) if post_type == 'reels' else 0
                    },
                    category=category,
                    metadata={
                        'iteration': self.iteration,
                        'event': event['name'],
                        'post_type': post_type,
                        'has_story': random.choice([True, False]),
                        'has_reels': post_type == 'reels',
                        'filter_used': random.choice(['none', 'clarendon', 'gingham', 'lark', 'moon'])
                    }
                )
                
                posts.append(post)
                self.post_id += 1
        
        return posts
    
    def _get_instagram_event_type(self) -> dict:
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


# ============================================
# TEST UNITAIRE
# ============================================

if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 70)
    print("📸 TEST INSTAGRAM COLLECTOR AVANCÉ")
    print("=" * 70)
    
    # Créer le collecteur
    collector = DynamicInstagramCollector()
    
    # Lancer 3 cycles de collecte
    for cycle in range(3):
        print(f"\n📊 CYCLE {cycle + 1}/3")
        
        posts = collector.collect_business_posts()
        
        # Afficher statistiques
        print(f"✅ Posts collectés: {len(posts)}")
        
        # Afficher quelques exemples
        print(f"\n📝 EXEMPLES:")
        for i, post in enumerate(posts[:3]):
            print(f"\n{i+1}. [{post.category.value.upper()}]")
            print(f"   Content: {post.content[:80]}...")
            print(f"   Author: {post.author} ({post.author_followers:,} followers)")
            print(f"   Likes: {post.metrics['likes']:,} | Comments: {post.metrics.get('comments', 0):,}")
            print(f"   Type: {post.metadata.get('post_type', 'feed')}")
        
        print("-" * 70)
        
        # Distribution par catégorie
        categories = {}
        for post in posts:
            cat = post.category.value
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n🏷️  DISTRIBUTION:")
        for cat, count in categories.items():
            percentage = (count / len(posts)) * 100
            print(f"   • {cat:15} → {count:2} posts ({percentage:.1f}%)")
        
        # Pause entre cycles
        if cycle < 2:
            import time
            time.sleep(2)
    
    print("\n" + "=" * 70)
    print("✅ TEST INSTAGRAM COLLECTOR TERMINÉ")
    print("=" * 70)