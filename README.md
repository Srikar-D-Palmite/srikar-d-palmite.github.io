# LINKIT
#### Video Demo:  <https://youtu.be/SiCQ1625hmo>
#### Description:
linkit is a social media website where users can post hyperlinks to websites they find interesting or useful.
It was created with the aim of spreading awareness of fun and useful websites. Unlike
search engines, it provides the websites that people have personally recommended. This
allows people to express their interests and find interesting new websites they never
knew existed.

###### User Experience:
First, users will be greeted with a home page containing the latest posts on the website.
They can register an account, or search up some posts right away. The registration process requires
a unique username (not taken already), and the username and password have to be atleast 4 characters
long. This ensures security and fairness. The user will have a unique id in the users table in the database.
After registering, they must log onto the site. Once logged in, they will see and be able to access many more
features from the navigation bar on the top of the site.
The *navigation bar* can direct you to your post history, a search feature, a page where the user can
post themselves, a page with their friends names, a page where they can ask other users to become
their friend, and a page to accept friend requests. The bar stays in place a the top of
the screen when users scroll down. The cs50 button leads them to Harvard's cs50x website.
In the *post* page, users have to fill up a form to post their own website link publicly on
the website. The inputs are the domain (hyperlink to the website. Required), a description on what
the website is useful for or contains, and tags to allow others to find their post when searching
for similar websites. The post is stored in a table in the database, with other info like the date,
time, and id of the user who posted it.
The *history* feature shows all the user's posts in decending order of date and time posted. They
can see the number of views it got from users other than themselves. They also have the option to
permanently delete the post.
The *search* feature allows a user, even non-registered ones, for their convenience, to search up
websites posted by other users by the site's name, description, and tags.
The *friends* page will show a list of your friends, and allow you to see their post history by clicking
on their name.
You can also make friend requests on the *add friends* page by simply submitting their username.
Of course, there is also a feature to *accept* friend requests.
There are several other tiny details which add to the experience, such as titles on anchor tags
to inform new users about what clicking on a link/button does. The website does not have any
tutorial on how to use it, a purposely chosen design choice. The user can learn on his/her
own how to use it. This adds to the immersion aspect, as seen from the
[super mario effect](https://www.youtube.com/watch?v=9vJRopau0g0).
While building the website, I had to make many decisions on how I wanted it to look and function.
I had to choose how to display the posts, eventually settling on using a table and making it
similar to reddit. I also had to think very hard in some parts, such as how to design a search
algorithm, or where or I wanted to display certain features like view count.

##### Styling:
Many styling choices have been specifically made for the website. Linkit is designed to look
minimalistic. There aren't any backgrounds nor many pictures. Apart from the navigation bar at the top,
there is a white background, with only text and sometimes tables, in the body of the site.
Additionally, there is a footer at the bottom that stays in place as you scroll up or down. This comprises
the basic layout of the site. The theme colors used are a blue (#004f99) and an orange (#f2800d).

##### Features:
- Creating an account
- Viewing the latest posts
- Posting hyperlinks
- Deleting your posts
- View counter for each post
- Searching key words to find links to websites
- See your posting history in order from latest to oldest
- Add Friends and see their posts