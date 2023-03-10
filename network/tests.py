from django.test import TestCase, Client
from .models import User, Follow, Post, Like
from .forms import NewPostForm
from django.core.paginator import Page

# Create your tests here.

class NetworkTestCase(TestCase):

    def setUp(self):

        # Create Users
        user1 = User.objects.create_user("abby_1", "abby@django.com", "123")
        user2 = User.objects.create_user("brandon_2", "brandon@django.com", "123")
        user3 = User.objects.create_user("charlie_3", "charlie@django.com", "123")

        # Create Follower/Following relationship
        # 1 follows user 2 and 3
        Follow.objects.create(user=user1, followed=user2)
        Follow.objects.create(user=user1, followed=user3)

        # 2 follows 3
        Follow.objects.create(user=user2, followed=user3)

        # Create Posts
        # User1 Posts
        post_a1 = Post.objects.create(author=user1, content="FOO")

        # User2 Posts
        post_b1 = Post.objects.create(author=user2, content="BAR")
        post_b2 = Post.objects.create(author=user2, content="BAZ")

        # Like Posts
        Like.objects.create(user=user1, post=post_b1)
        Like.objects.create(user=user3, post=post_b1)


    # 1. Test following count
    def test_following_count(self):
        user_a = User.objects.get(username="abby_1")
        user_b = User.objects.get(username="brandon_2")
        user_c = User.objects.get(username="charlie_3")

        self.assertEqual(user_a.following.count(), 2)
        self.assertEqual(user_b.following.count(), 1)
        self.assertEqual(user_c.following.count(), 0)
        

    # 2. Test followers count
    def test_follower_count(self):
        user_a = User.objects.get(username="abby_1")
        user_b = User.objects.get(username="brandon_2")
        user_c = User.objects.get(username="charlie_3")

        self.assertEqual(user_a.follower.count(), 0)
        self.assertEqual(user_b.follower.count(), 1)
        self.assertEqual(user_c.follower.count(), 2)


    # 3. Test following usernames
    def test_following_username(self):
        user_a = User.objects.get(username="abby_1")
        user_a_following_set = Follow.objects.filter(user=user_a).all()
        self.assertEqual(user_a_following_set[0].followed.username, "brandon_2")
        self.assertEqual(user_a_following_set[1].followed.username, "charlie_3")
    

    # 4. Test follower usernames
    def test_follower_username(self):
        user_c = User.objects.get(username="charlie_3")
        user_c_followed_set = Follow.objects.filter(followed=user_c).all()
        self.assertEqual(user_c_followed_set[0].user.username, 'abby_1')
        self.assertEqual(user_c_followed_set[1].user.username, 'brandon_2')


    # 5. Test post count
    def test_post_count(self):
        user_a = User.objects.get(username="abby_1")
        user_a_posts = Post.objects.filter(author=user_a)

        user_b = User.objects.get(username="brandon_2")
        user_b_posts = Post.objects.filter(author=user_b)

        user_c = User.objects.get(username="charlie_3")
        user_c_posts = Post.objects.filter(author=user_c)

        self.assertEqual(user_a_posts.count(), 1)
        self.assertEqual(user_b_posts.count(), 2)
        self.assertEqual(user_c_posts.count(), 0)


    # 6. Test Like Counts
    def test_like_count(self):

        # Get Users
        user_a = User.objects.get(username="abby_1")
        user_b = User.objects.get(username="brandon_2")
        user_c = User.objects.get(username="charlie_3")

        # Get Posts
        user_b_posts = Post.objects.filter(author=user_b)

        self.assertEqual(Like.objects.filter(post=user_b_posts[0]).count(), 2)
        self.assertEqual(Like.objects.filter(post=user_b_posts[1]).count(), 0)

        # Delete Like
        like_1 = Like.objects.get(user=user_a, post=user_b_posts[0])
        like_1.delete()
        
        self.assertEqual(user_b_posts[0].like_objs.count(), 1)
    

    # 7. Test if post is Likable
    def test_likable_false(self):

        # Get Users
        user_a = User.objects.get(username="abby_1")
        user_b = User.objects.get(username="brandon_2")
        user_c = User.objects.get(username="charlie_3")

        # Get Posts
        user_b_posts = Post.objects.filter(author=user_b)

        # Assert user cannot like a post more than once
        self.assertFalse(user_b_posts[0].likable(user_a))

    # 8. Test if post is Likable
    def test_likable_true(self):

        # Get Users
        user_a = User.objects.get(username="abby_1")
        user_b = User.objects.get(username="brandon_2")
        user_c = User.objects.get(username="charlie_3")

        # Get Posts
        user_b_posts = Post.objects.filter(author=user_b)

        # Assert user can like post if not already liked
        self.assertTrue(user_b_posts[1].likable(user_a))

    # 9. Test index page and context
    def test_index(self):
        c = Client()
        response = c.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context["form"], NewPostForm))
        self.assertEqual(response.context["page_obj"].__len__(), 1)

    # 10. Test Profile page and context
    def test_profile(self):

        # Get Users
        user_a = User.objects.get(username="abby_1")
        user_b = User.objects.get(username="brandon_2")
        user_c = User.objects.get(username="charlie_3")

        c = Client()

        # Client Login
        login = c.login(username=user_c.username, password="123")

        response = c.get(f'/profile/{user_a.username}')

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile_user_following"].count(), 2)
        self.assertEqual(response.context["profile_user_followers"].count(), 0)
        self.assertEqual(response.context["profile_user_obj"], user_a)
        self.assertEqual(response.context["requester_followers"].count(), 2)
        self.assertTrue(isinstance(response.context["page_obj"], Page))


    # Test follow API
    # for Follow
    def test_follow(self):
        
        # Get Users
        user_a = User.objects.get(username="abby_1")
        user_b = User.objects.get(username="brandon_2")
        user_c = User.objects.get(username="charlie_3")

        c = Client()

        # Client Login
        c.login(username=user_c.username, password="123")

        # Ensure User C following 0 people
        user_c_following = Follow.objects.filter(user=user_c)
        self.assertEqual(user_c_following.count(), 0)

        # Have User C follow User A
        response = c.put('/follow/', {
            "action": "follow",
            "target_username": user_a.username
            })

        # Check User A follow count is now 1
        user_a_followers = Follow.objects.filter(followed=user_a)
        self.assertEqual(user_a_followers.count(), 1)

        # Check User C following count is now 1
        user_c_following = Follow.objects.filter(user=user_c)
        self.assertEqual(user_c_following.count(), 1)



    # for Unfollow
