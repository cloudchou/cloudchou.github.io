---
layout: default
css: ['sidebar-post-nav.css','post.css']
---

{% include jumbotron-post.html %}

<article class="post container" itemscope itemtype="http://schema.org/BlogPosting">
    <p>本文原创作者:<a href="http://weibo.com/muguachou" target="_blank">Cloud Chou</a>. 欢迎转载，请注明出处和<a href="{{ site.url }}{{ page.url }}" target="_blank">本文链接</a></p>

    <div class="row">

        {% if page.no-post-nav %}
        <div class="col-md-12 markdown-body">

            {{ content }}

            <!-- Comments -->
            {% include disqus-comments.html %}
        </div>
        {% else %}
        <div class="col-md-8 markdown-body">

            {{ content }}

            <!-- pay -->
            {% include pay.html %}

            <!-- Comments -->
            {% include comments.html %}
        </div>

        <div class="col-md-4">
            {% include sidebar-post-nav.html %}
        </div>
        {% endif %}

    </div>


</article>