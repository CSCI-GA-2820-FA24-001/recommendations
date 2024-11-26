$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    /// Clears all form fields
    function clear_form_data() {
        $("#rec_id").val("");
        $("#rec_user_id").val("");
        $("#rec_product_id").val("");
        $("#rec_score").val("");
        $("#rec_num_of_likes").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************

    $("#create-btn").click(function () {
        var userId = $("#rec_user_id").val();
        var productId = $("#rec_product_id").val();
        var score = $("#rec_score").val();
        var numLikes = $("#rec_num_likes").val();
        var timestamp = new Date().toISOString(); // Auto-generate timestamp
    
        let data = {
            "user_id": userId,
            "product_id": productId,
            "score": score,
            "num_likes": numLikes,
            "timestamp": timestamp,
        };
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });
    
        ajax.done(function (res) {
            // Display the new recommendation's ID if needed
            flash_message(`Success! New Recommendation ID: ${res.id}`);
        });
    
        ajax.fail(function (res) {
            flash_message(res.responseJSON.message || "Error creating recommendation");
        });
    });


    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        let rec_id = $("#rec_id").val();
        let product_id = parseInt($("#rec_product_id").val());
        let user_id = parseInt($("#rec_user_id").val());
        let num_likes = parseInt($("#rec_num_of_likes").val());
        let score = parseFloat($("#rec_score").val());
        let timestamp = new Date().toISOString(); // Auto-generate the current timestamp

        let data = {
            "id": rec_id,
            "product_id": product_id,
            "user_id": user_id,
            "score": score,
            "num_likes": num_likes,
            "timestamp": timestamp
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/recommendations/${rec_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        let rec_id = $("#rec_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/recommendations/${rec_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            // console.log(res)
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });
    // ****************************************
    // Retrieve a Recommendation by src-item-id
    // ****************************************
    $("#retrieve-by-src-item-id-btn").click(function () {
        let rec_src_item_id = $("#rec_src_item_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/recommendations/source-product?source_item_id=${rec_src_item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            // console.log(res)
            if (res.length > 0) {
                update_form_data(res[0]) // src-item-id is not a unique id, so only update the form with the first returned value
                recQuery()
                flash_message("Success")
            }
            else {
                flash_message("No recommendations found!")
            }
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });
    // ****************************************
    // Delete a Recommendation
    // ****************************************

    $("#delete-btn").click(function () {

        let rec_id = $("#rec_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/recommendations/${rec_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Recommendation has been deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#flash_message").empty();
        clear_form_data()
    });

    $("#search-btn").click(function () {
        recQuery()
    });
})