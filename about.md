---
layout: default
menu: home
css: ['index.css', 'sidebar-cv.css','styles.css']
js: ['sidebar.js','404.js']
---

{% include jumbotron.html %}

<section class="content container">

    <div class="row">

        <!-- Post List -->
        <div class="col-md-8 main-wrapper">

            {% include carrier-profile.html %}


            {% include experience.html %}

            {% include projects.html %}

            {% include skills.html %}
        </div>


        <div class="col-md-4">
            {% include about-sidebar-cv.html %}
        </div>

    </div>

</section>

