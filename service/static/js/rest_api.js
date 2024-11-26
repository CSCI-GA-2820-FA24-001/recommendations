$(function () {
    // ****************************************
    //  Utility Functions
    // ****************************************

    // Clears all form fields
    function clear_form_data() {
        $("#rec_id, #rec_user_id, #rec_product_id, #rec_score, #rec_num_likes").val("");
    }

    // Updates the flash message area with styling
    function flash_message(message, type = "success") {
        const messageClass = type === "success" ? "flash-success" : "flash-error";
        $("#flash_message").html(
            `<div class="flash-message ${messageClass}">${message}</div>`
        );
    }

    // Validates form data before submission
    function validate_form(data) {
        if (!data.user_id || isNaN(data.user_id)) {
            flash_message("User ID must be a valid number", "error");
            return false;
        }
        if (!data.product_id || isNaN(data.product_id)) {
            flash_message("Product ID must be a valid number", "error");
            return false;
        }
        if (!data.score || isNaN(data.score) || data.score < 0 || data.score > 5) {
            flash_message("Score must be a number between 0 and 5", "error");
            return false;
        }
        if (!data.num_likes || isNaN(data.num_likes)) {
            flash_message("Number of Likes must be a valid number", "error");
            return false;
        }
        return true;
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************
    $("#create-btn").click(function () {
        const data = {
            user_id: $("#rec_user_id").val(),
            product_id: $("#rec_product_id").val(),
            score: $("#rec_score").val(),
            num_likes: $("#rec_num_likes").val(),
            timestamp: new Date().toISOString(), // Auto-generate timestamp
        };

        if (!validate_form(data)) return;

        $("#flash_message").empty();

        $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        })
            .done(function (res) {
                $("#rec_id").val(res.id); // Set the ID field in the form
                flash_message("Success");
            })
            .fail(function (res) {
                flash_message(res.responseJSON.message || "Error creating recommendation", "error");
            });
    });

    // ****************************************
    // Update a Recommendation
    // ****************************************
    $("#update-btn").click(function () {
        const rec_id = $("#rec_id").val();
        const data = {
            user_id: $("#rec_user_id").val(),
            product_id: $("#rec_product_id").val(),
            score: $("#rec_score").val(),
            num_likes: $("#rec_num_likes").val(),
            timestamp: new Date().toISOString(), // Auto-generate timestamp
        };

        if (!rec_id) {
            flash_message("Recommendation ID is required for update", "error");
            return;
        }

        if (!validate_form(data)) return;

        $.ajax({
            type: "PUT",
            url: `/recommendations/${rec_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        })
            .done(function (res) {
                flash_message("Success");
            })
            .fail(function (res) {
                flash_message(res.responseJSON.message || "Error updating recommendation", "error");
            });
    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************
    $("#retrieve-btn").click(function () {
        const rec_id = $("#rec_id").val();

        if (!rec_id) {
            flash_message("Recommendation ID is required to retrieve data", "error");
            return;
        }

        $.ajax({
            type: "GET",
            url: `/recommendations/${rec_id}`,
        })
            .done(function (res) {
                $("#rec_user_id").val(res.user_id);
                $("#rec_product_id").val(res.product_id);
                $("#rec_score").val(res.score);
                $("#rec_num_likes").val(res.num_likes);
                flash_message("Success");
            })
            .fail(function (res) {
                clear_form_data();
                flash_message(res.responseJSON.message || "Error retrieving recommendation", "error");
            });
    });

    // ****************************************
    // Delete a Recommendation
    // ****************************************
    $("#delete-btn").click(function () {
        const rec_id = $("#rec_id").val();

        if (!rec_id) {
            flash_message("Recommendation ID is required to delete data", "error");
            return;
        }

        $.ajax({
            type: "DELETE",
            url: `/recommendations/${rec_id}`,
        })
            .done(function () {
                clear_form_data();
                flash_message("Success");
            })
            .fail(function (res) {
                flash_message(res.responseJSON.message || "Error deleting recommendation", "error");
            });
    });

    // ****************************************
    // Search Recommendations
    // ****************************************
    $("#search-btn").click(function () {
        const user_id = $("#rec_user_id").val();
        const product_id = $("#rec_product_id").val();
        const queryParams = [];

        if (user_id) queryParams.push(`user_id=${user_id}`);
        if (product_id) queryParams.push(`product_id=${product_id}`);

        const queryString = queryParams.length ? `?${queryParams.join("&")}` : "";

        $.ajax({
            type: "GET",
            url: `/recommendations/filter${queryString}`,
        })
            .done(function (res) {
                $("#search_results").empty();
                if (res.length === 0) {
                    flash_message("No recommendations found.", "error");
                    return;
                }

                let table = `<table class="table table-striped"><thead>
                                <tr>
                                    <th>ID</th>
                                    <th>User ID</th>
                                    <th>Product ID</th>
                                    <th>Score</th>
                                    <th>Number of Likes</th>
                                    <th>Timestamp</th>
                                </tr>
                             </thead><tbody>`;

                res.forEach((rec) => {
                    table += `<tr>
                                <td>${rec.id}</td>
                                <td>${rec.user_id}</td>
                                <td>${rec.product_id}</td>
                                <td>${rec.score}</td>
                                <td>${rec.num_likes}</td>
                                <td>${rec.timestamp}</td>
                              </tr>`;
                });

                table += `</tbody></table>`;
                $("#search_results").append(table);
                flash_message("Success");
            })
            .fail(function (res) {
                flash_message(res.responseJSON.message || "Error performing search", "error");
            });
    });

    // ****************************************
    // Clear the Form
    // ****************************************
    $("#clear-btn").click(function () {
        clear_form_data();
        flash_message("Form cleared successfully.");
    });

    $("#search-btn").click(function () {
        recQuery()
    });

    // ****************************************
    // Like a Recommendation
    // ****************************************
    $("#like-btn").click(function () {
        let recommendation_id = $("#recommendation_id").val();
        
        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/recommendations/${recommendation_id}/likes`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });
})
