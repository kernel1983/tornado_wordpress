
$ ->
    post_id_from = POST_ID_FROM
    carousel_template = _.template($('#carousel-template').html())

    load_more = () ->
        #console.log post_id_from
        $.getJSON "/api/more?from="+post_id_from+TERM, (data) ->
            for i in data["list"]
                $("#post_list").append(carousel_template(i))
            post_id_from = data["post_id_from"]

    $('.carousel').carousel
        interval: 3000
        pause: null

    $(window).endlessScroll
        fireOnce: true
        fireDelay: true
        loader: "<div class='loading'>LOADING...<div>"
        callback: (p) -> load_more()
