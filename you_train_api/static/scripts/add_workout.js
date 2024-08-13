// Delegates click events for "Add Exercise" buttons to open the exercise modal
document.getElementById('segment-form').addEventListener('click', function(event) {
    if (event.target && event.target.classList.contains('add-exercise')) {
        var modal = document.getElementById('exercise-modal');
        modal.style.display = "block";

        // Load exercises based on the current query
        loadExercises('');

        // Handle search button click for filtering exercises
        document.getElementById('search-button').onclick = function() {
            var query = document.getElementById('search-query').value;
            loadExercises(query);
        };
    }
});

// Saves exercise details when "Save" button is clicked
document.getElementById('save-exercise-details').addEventListener('click', function() {
    saveExerciseDetails(false);
});

// Saves exercise details and closes modal when "Save and Add Next" button is clicked
document.getElementById('save-add-next-exercise-details').addEventListener('click', function() {
    saveExerciseDetails(true);
});

// Closes the exercise details modal and returns to the exercise selection modal
document.getElementById('back-to-exercises').addEventListener('click', function() {
    document.getElementById('exercise-details-modal').style.display = "none";
    document.getElementById('exercise-modal').style.display = "block";
});


// Closes the exercise modal when the close button is clicked
document.querySelector('.close').onclick = function() {
    document.getElementById('exercise-modal').style.display = "none";
};

// Closes the exercise details modal when the close button is clicked
document.querySelector('.close-details').onclick = function() {
    document.getElementById('exercise-details-modal').style.display = "none";
};


window.onclick = function(event) {
    if (event.target == document.getElementById('exercise-modal')) {
        document.getElementById('exercise-modal').style.display = "none";
    }
    if (event.target == document.getElementById('exercise-details-modal')) {
        document.getElementById('exercise-details-modal').style.display = "none";
    }
};

function saveExerciseDetails(addNext) {
    var reps = document.getElementById('reps').value;
    var duration_0 = document.getElementById('duration_0').value;
    var duration_1 = document.getElementById('duration_1').value;
    var duration_2 = document.getElementById('duration_2').value;
    var rest_time_m = document.getElementById('rest_time_0').value || '00';
    var rest_time_s = document.getElementById('rest_time_1').value || '00';
    var notes = document.getElementById('notes').value;

    // Validate that either reps or duration is filled, but not both
    if ((reps && (duration_0 || duration_1 || duration_2)) || (!reps && (!duration_0 && !duration_1 && !duration_2))) {
        console.log(`Reps: ${reps}, Duration: ${duration_0}:${duration_1}:${duration_2}`);

        alert('Either reps or duration must be specified, but not both.');
        return;
    }

    // Set duration fields to '00' if not provided
    duration_m = duration_1.padStart(2, '0') || '00';
    duration_s = duration_2.padStart(2, '0') || '00';

    if (!reps) {
        duration_0 = duration_0 || '00';
    }

 var exerciseTableBody = document.getElementById('exercise-table-body');
    if (!exerciseTableBody) {
        console.error('Exercise table body not found');
        return;
    }

    var exercise = document.getElementById('selected-exercise-id').value;
    var exerciseName = document.getElementById('exercise-details-title').textContent;
    var durationString = reps ? '' : `${duration_h}:${duration_m}:${duration_s}`;

    var newExerciseRow = document.createElement('tr');
    newExerciseRow.innerHTML = `
        <td>${exerciseName}</td>
        <td>${reps}</td>
        <td>${durationString}</td>
        <td>${rest_time_m}:${rest_time_s}</td>
        <td>${notes}</td>
    `;

    // Generate formset index and add hidden inputs for new exercise
    var formsetIndex = document.getElementById('id_exercises-TOTAL_FORMS').value;
    console.log('Formset index:', formsetIndex)
    console.log("${duration_0}:${duration_1}:${duration_2}")
    var hiddenInputs = `
        <input type="hidden" name="exercises-${formsetIndex}-exercise" value="${exercise}">
        <input type="hidden" name="exercises-${formsetIndex}-reps" value="${reps || 1}">
        <input type="hidden" name="exercises-${formsetIndex}-duration" value="${durationString}">
        <input type="hidden" name="exercises-${formsetIndex}-rest_time" value="${rest_time_m}:${rest_time_s}">
        <input type="hidden" name="exercises-${formsetIndex}-notes" value="${notes}">
    `;
    newExerciseRow.innerHTML += hiddenInputs;

    exerciseTableBody.appendChild(newExerciseRow);

    // Update the total form count
    document.getElementById('id_exercises-TOTAL_FORMS').value = parseInt(formsetIndex) + 1;

    if (!addNext) {
        document.getElementById('exercise-details-modal').style.display = "none";
    }

    // Optionally submit the form if this is the final exercise
    // if (!addNext) {
    //     document.getElementById('segment-form').submit();
    // }

    resetExerciseDetailsForm();
}

function resetExerciseDetailsForm() {
    document.getElementById('reps').value = '';
    document.getElementById('duration_0').value = '';
    document.getElementById('duration_1').value = '';
    document.getElementById('duration_2').value = '';
    document.getElementById('rest_time_0').value = '';
    document.getElementById('rest_time_1').value = '';
    document.getElementById('notes').value = '';
}

function loadExercises(query) {
    fetch(`/exercise_search/?query=${query}`)
        .then(response => response.json())
        .then(data => {
            var exerciseList = document.getElementById('exercise-list');
            exerciseList.innerHTML = '';
            data.forEach(exercise => {
                var exerciseItem = document.createElement('div');
                exerciseItem.textContent = exercise.name;
                exerciseItem.onclick = function() {
                    document.getElementById('selected-exercise-id').value = exercise.id;
                    document.getElementById('exercise-details-title').textContent = `${exercise.name}`;
                    document.getElementById('exercise-modal').style.display = "none";
                    document.getElementById('exercise-details-modal').style.display = "block";
                };
                exerciseList.appendChild(exerciseItem);
            });
        });
}

// save workout
// document.getElementById('save-segment').addEventListener('click', function(event) {
//     event.preventDefault(); // Prevent default form submission
//
//     var segmentForm = document.querySelector('.segment-form');
//     var isValid = true;
//
//     // Get values from the segment form
//     var restTimeMinutes = segmentForm.querySelector('input[id^="seg_rest_time_"][id$="_0"]').value;
//     var restTimeSeconds = segmentForm.querySelector('input[id^="seg_rest_time_"][id$="_1"]').value;
//     // var reps = segmentForm.querySelector('input[name$="reps"]').value;
//     var exerciseRows = segmentForm.querySelectorAll('tbody tr'); // Rows with exercises in the segment
//
//     // Log the segment and exercise count
//     console.log(`Segment has ${exerciseRows.length} exercises`);
//
//     // Validate form fields
//     if (!reps) {
//         isValid = false;
//         alert('All required fields must be filled out.');
//     }
//
//     if (exerciseRows.length === 0) {
//         isValid = false;
//         alert('There needs to be at least 1 exercise in the segment.');
//     }
//
//     if (isValid) {
//         console.log('Form is valid. Number of exercises:', exerciseRows.length);
//         document.getElementById('workout-segment-form').submit();
//     }
// });
