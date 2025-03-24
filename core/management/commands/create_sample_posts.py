from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Post, Category
from django.utils.text import slugify
from django.db import transaction
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create sample blog posts'

    def handle(self, *args, **options):
        try:
            admin_user = User.objects.get(email='admin@gmail.com')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user not found! Please create admin user first.'))
            return

        # Create categories
        categories = {
            'Technology': 'Latest in tech and innovation',
            'Personal Development': 'Growth and self-improvement',
            'Travel': 'Exploring the world',
            'Health': 'Wellness and healthy living',
            'Finance': 'Money management and investing'
        }

        created_categories = {}
        for name, description in categories.items():
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name)}
            )
            created_categories[name] = category
            if created:
                self.stdout.write(f'Created category: {name}')

        # Blog posts data
        posts_data = [
            {
                'title': 'The Future of Artificial Intelligence: Beyond the Hype',
                'content': '''
                Artificial Intelligence has become an integral part of our daily lives, but what lies ahead? This post explores the realistic possibilities and challenges of AI technology.

                Key Areas of AI Development:
                - Machine Learning Evolution
                - Natural Language Processing
                - Robotics and Automation
                - Ethical AI Considerations

                The impact of AI extends beyond just technological advancement. It's reshaping industries, creating new job opportunities, and raising important ethical questions about the future of human-machine interaction.

                As we look to the future, it's crucial to understand both the potential and limitations of AI technology. While AI continues to make remarkable progress, human creativity and emotional intelligence remain irreplaceable.

                Let's embrace AI's potential while ensuring its development aligns with human values and ethical principles.
                ''',
                'category': 'Technology'
            },
            {
                'title': 'Building Healthy Habits That Last',
                'content': '''
                Creating lasting habits is the key to sustainable personal growth. This guide explores proven strategies for building habits that stick.

                The Habit Formation Process:
                1. Start Small: Begin with tiny, manageable changes
                2. Create Triggers: Link new habits to existing routines
                3. Track Progress: Monitor your consistency
                4. Celebrate Small Wins: Reward yourself for progress

                Remember, habit formation takes time and patience. Research suggests it takes anywhere from 21 to 66 days to form a new habit, depending on complexity and individual factors.

                Focus on progress, not perfection. Each small step forward is a victory in your personal development journey.

                By understanding and applying these principles, you can create positive changes that last a lifetime.
                ''',
                'category': 'Personal Development'
            },
            {
                'title': 'Hidden Gems of Southeast Asia',
                'content': '''
                Beyond the popular tourist destinations lie countless hidden treasures in Southeast Asia. Let's explore some lesser-known but equally magnificent locations.

                Must-Visit Hidden Locations:
                - Phong Nha Caves, Vietnam
                - Bantayan Island, Philippines
                - Kampong Ayer, Brunei
                - Mrauk U, Myanmar

                These destinations offer authentic cultural experiences, stunning natural beauty, and fewer tourists than their more famous counterparts.

                Travel Tips:
                - Best times to visit
                - Local transportation options
                - Accommodation recommendations
                - Cultural etiquette

                Experience the true essence of Southeast Asia through these undiscovered paradises.
                ''',
                'category': 'Travel'
            },
            {
                'title': 'Mindful Eating: A Path to Better Health',
                'content': '''
                Mindful eating isn't just about what you eat, but how you eat. This comprehensive guide explores the principles and benefits of mindful eating.

                Core Principles:
                - Eating with attention and intention
                - Recognizing hunger and fullness cues
                - Understanding emotional eating
                - Making conscious food choices

                The benefits extend beyond weight management to include better digestion, improved relationship with food, and enhanced overall well-being.

                Practical Tips:
                1. Eat without distractions
                2. Chew thoroughly
                3. Use all your senses
                4. Practice gratitude for your food

                Transform your relationship with food through mindfulness.
                ''',
                'category': 'Health'
            },
            {
                'title': 'Smart Investment Strategies for Beginners',
                'content': '''
                Starting your investment journey can be overwhelming. This guide breaks down essential strategies for beginner investors.

                Investment Basics:
                - Understanding risk tolerance
                - Diversification principles
                - Long-term vs. short-term investing
                - Common investment vehicles

                Key Steps for Beginners:
                1. Start with emergency savings
                2. Understand your investment goals
                3. Research different investment options
                4. Start small and learn continuously

                Remember: Investing is a marathon, not a sprint. Focus on building a solid foundation for your financial future.
                ''',
                'category': 'Finance'
            },
            {
                'title': 'Sustainable Tech: Green Innovation for the Future',
                'content': '''
                Exploring how technology is driving environmental sustainability and creating a greener future.

                Key Areas of Green Tech:
                - Renewable Energy Innovations
                - Sustainable Transportation
                - Smart City Solutions
                - Eco-friendly Manufacturing

                Current innovations are not just about reducing environmental impact; they're about creating sustainable solutions that benefit both the planet and its inhabitants.

                The future of technology lies in sustainable innovation. By embracing these solutions, we can create a better world for future generations.
                ''',
                'category': 'Technology'
            },
            {
                'title': 'The Art of Digital Minimalism',
                'content': '''
                In an increasingly connected world, digital minimalism offers a path to better focus and reduced stress.

                Core Principles:
                - Intentional technology use
                - Digital decluttering
                - Creating healthy boundaries
                - Mindful consumption of content

                Practical Steps:
                1. Audit your digital life
                2. Eliminate unnecessary apps
                3. Set specific usage times
                4. Create tech-free zones

                By embracing digital minimalism, you can reclaim your time and attention while maintaining productivity.
                ''',
                'category': 'Personal Development'
            },
            {
                'title': 'Urban Gardening: Growing Food in Small Spaces',
                'content': '''
                Transform your limited urban space into a thriving garden. This guide shows you how to start and maintain an urban garden.

                Essential Elements:
                - Choosing the right plants
                - Maximizing space usage
                - Soil and container selection
                - Light and water management

                Best Plants for Urban Gardens:
                1. Herbs (basil, mint, parsley)
                2. Leafy greens
                3. Tomatoes
                4. Vertical growing vegetables

                Urban gardening isn't just about growing food; it's about creating a sustainable and healthy lifestyle in the city.
                ''',
                'category': 'Health'
            },
            {
                'title': 'Cryptocurrency: Understanding the Basics',
                'content': '''
                Demystifying cryptocurrency and blockchain technology for beginners.

                Key Concepts:
                - Blockchain fundamentals
                - Different types of cryptocurrencies
                - Security considerations
                - Investment basics

                Important Considerations:
                1. Understanding market volatility
                2. Security best practices
                3. Regulatory environment
                4. Risk management

                While cryptocurrency offers exciting possibilities, it's crucial to approach it with knowledge and caution.
                ''',
                'category': 'Finance'
            },
            {
                'title': 'Remote Work Revolution: The New Normal',
                'content': '''
                Exploring how remote work is reshaping the future of employment and professional life.

                Key Aspects:
                - Digital collaboration tools
                - Work-life balance strategies
                - Productivity techniques
                - Team building in virtual environments

                Best Practices:
                1. Creating a dedicated workspace
                2. Maintaining regular schedules
                3. Effective communication strategies
                4. Managing remote teams

                Remote work isn't just a temporary solution; it's becoming a permanent part of our professional landscape.
                ''',
                'category': 'Technology'
            }
        ]

        # Create posts
        with transaction.atomic():
            base_date = datetime.now() - timedelta(days=len(posts_data))
            
            for index, post_data in enumerate(posts_data):
                post = Post.objects.create(
                    title=post_data['title'],
                    slug=slugify(post_data['title']),
                    content=post_data['content'].strip(),
                    author=admin_user,
                    category=created_categories[post_data['category']],
                    created_at=base_date + timedelta(days=index)
                )
                self.stdout.write(f'Created post: {post.title}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample blog posts!')) 