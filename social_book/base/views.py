import random
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib import messages
from itertools import chain

from .models import Profile, Post, LikePost, FollowersCount


@login_required(login_url='sign-in')
def index(request):

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)
    
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))


    # ----------> users suggestion system <----------
    all_users = User.objects.all()
    user_following_all = []
    
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]

    # remove current user from suggestions
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)
    
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)
    
    suggestion_profile_list = list(chain(*username_profile_list))
    for suggestion in suggestion_profile_list:
        print(suggestion.user)

    return render(request, 'index.html', {
            'user_profile': user_profile, 
            'posts': feed_list,
            'suggestion_profile_list': suggestion_profile_list[:4],
        }
    )


def sign_up(request):

    if request.method != 'POST':
        return render(request, 'signup.html')
    
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password2 = request.POST['password2']

        # empty field validation
    if username == '':
        messages.info(request, 'Empty field: username')
        return redirect('sign-up')
        
    if email == '':
        messages.info(request, 'Empty field: email')
        return redirect('sign-up')

    if password == '':
        messages.info(request, 'Empty field: password')
        return redirect('sign-up')

        # confirmation password 
    if password != password2:
        messages.error(request, 'Passwords does not match')
        return redirect('sign-up')
        
        # existed user validation
    is_email_exist = User.objects.filter(email=email).exists()
    if is_email_exist:
        messages.info(request, f'{email} already registred')
        return redirect('sign-up')

    is_username_exist = User.objects.filter(username=username).exists()
    if is_username_exist:
        messages.info(request, f'Username {username} already taken')
        return redirect('sign-up')
        
    user = User.objects.create_user(
        username=username,
        email=email,
        password = password
    )
    user.save()

    # log user in and redirect to settings page
    user_login = auth.authenticate(username=username, password=password)
    auth.login(request, user_login)

    #create a Profile object for the new user
    user_model = User.objects.get(username=username)
    Profile.objects.create(
        user=user_model, 
        id_user=user_model.id
    ).save()

    return redirect('settings')

        
def sign_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)

        if user is None:
            messages.info(request, 'Invalid credentiasl')
            return redirect('sign-in')
        
        auth.login(request, user)
        return redirect('/')

    else:
        return render(request, 'signin.html')


@login_required(login_url='sign-in')
def logout(request):
    auth.logout(request)
    return redirect('sign-in')


@login_required(login_url='sign-in')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profile_image
            user_profile.profile_image = image
        else:
            user_profile.profile_image = request.FILES.get('image')
        
        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': user_profile})


@login_required(login_url='sign-in')
def uploads(request):
    if request.method != 'POST':
        return redirect('/')

    user = request.user.username
    image = request.FILES.get('image_upload')
    title = request.POST['title']

    Post.objects.create(
        user=user,
        image=image,
        title=title
    ).save()
    return redirect('/')


@login_required(login_url='sign-in')
def like_post(request):

    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(post_id=post_id)

    like_filter = LikePost.objects.filter(
        post_id=post_id, 
        username=username
    ).first()

    if like_filter is None:
        LikePost.objects.create(
            post_id=post_id, 
            username=username
        ).save()

        post.likes = post.likes+1
        post.save()
        return redirect('/')

    else:
        like_filter.delete()
        post.likes = post.likes-1
        post.save()
        return redirect('/')


@login_required(login_url='sign-in')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_amount= len(user_posts)
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    follower = request.user.username
    user = pk
    is_follow = FollowersCount.objects.filter(follower=follower, user=user).first()
    
    if is_follow:
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
        

    context = {
        'user_object':user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_amount': user_posts_amount,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='sign-in')
def follow(request):
    if request.method != 'POST':
        return redirect('/')
    
    follower = request.POST['follower']
    user = request.POST['user']

    is_follow = FollowersCount.objects.filter(
        follower=follower,
        user=user
    ).first()

    if is_follow:
        FollowersCount.objects.get(
            follower=follower,
            user=user,
        ).delete()
        return redirect(f'/profile/{user}')
    
    FollowersCount.objects.create(
        follower=follower,
        user=user
    ).save()
    return redirect(f'/profile/{user}')


@login_required(login_url='sign-in')
def search(request):
    if request.method != 'POST':
        return redirect('/')

    username = request.POST['username']

    
    username_object = User.objects.filter(username__icontains=username)
    username_profile = []
    username_profile_list = []

    for users in username_object:
        username_profile.append(users.id)
    
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)


    username_profile_list = list(chain(*username_profile_list))

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)


    return render(request, 'search.html', {
            'user_profile': user_profile,
            'username_profile_list': username_profile_list
        }
    )