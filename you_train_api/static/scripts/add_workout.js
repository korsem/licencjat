// Adds a new segment form when the "Add Segment" button is clicked
document.getElementById('add-segment').addEventListener('click', function() {
    var segmentFormset = document.getElementById('segment-formset');
    var newForm = segmentFormset.lastElementChild.cloneNode(true);
    var formIdx = segmentFormset.children.length;

    console.log(`Adding new segment with index ${formIdx}`);

    // Update form indices for inputs, textareas, and selects
    newForm.querySelectorAll('input, textarea, select').forEach(function(element) {
        var name = element.getAttribute('name');
        if (name) {
            var updatedName = name.replace(/-\d+-/g, `-${formIdx}-`);
            element.setAttribute('name', updatedName);
        }
        var id = element.getAttribute('id');
        if (id) {
            var updatedId = id.replace(/-\d+-/g, `-${formIdx}-`);
            element.setAttribute('id', updatedId);
        }
    });

    // Update button data-segment attributes
    newForm.querySelectorAll('button').forEach(function(button) {
        button.dataset.segment = formIdx;
    });

    // Clear existing exercise list in the new segment
    var exerciseList = newForm.querySelector('.exercise-list');
    exerciseList.innerHTML = '';

    // Remove any existing delete button to avoid duplication
    var existingDeleteButton = newForm.querySelector('.delete-segment');
    if (existingDeleteButton) {
        existingDeleteButton.remove();
    }

    // Create and append a new delete button for the new segment
    var deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'btn btn-danger delete-segment';
    deleteButton.textContent = 'Delete Segment';
    deleteButton.dataset.segment = formIdx;
    newForm.appendChild(deleteButton);

    // Attach event listener for the new delete button
    deleteButton.addEventListener('click', function() {
        newForm.remove();
    });

    segmentFormset.appendChild(newForm);

    // Log the updated number of segments
    console.log(`Number of segments: ${segmentFormset.children.length}`);
});

// Delegates click events for "Add Exercise" buttons to open the exercise modal
document.getElementById('segment-formset').addEventListener('click', function(event) {
    if (event.target && event.target.classList.contains('add-exercise')) {
        var segmentIndex = event.target.getAttribute('data-segment');
        var modal = document.getElementById('exercise-modal');
        modal.setAttribute('data-segment', segmentIndex);
        modal.style.display = "block";

        // Load exercises based on the current query
        loadExercises('');

        console.log(`Number of segments: ${document.getElementById('segment-formset').children.length}`);

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

// Logs a message when the workout form is submitted
document.getElementById('workout-form').addEventListener('submit', function(event) {
    console.log('Form is being submitted');
    // Uncomment to prevent default submission and debug
    // event.preventDefault();
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
    var duration_h = document.getElementById('duration_0').value;
    var duration_m = document.getElementById('duration_1').value;
    var duration_s = document.getElementById('duration_2').value;
    var rest_time_m = document.getElementById('rest_time_0').value;
    var rest_time_s = document.getElementById('rest_time_1').value;
    var notes = document.getElementById('notes').value;

    // Validate that either reps or duration is filled
    if (!reps && (!duration_h && !duration_m && !duration_s)) {
        alert('Either reps or duration must be specified.');
        return;
    }

    var segmentIndex = document.getElementById('exercise-modal').getAttribute('data-segment');

    console.log(`Saving exercise details for segment ${segmentIndex}`);
    var segmentForm = document.querySelectorAll('.segment-form')[segmentIndex];
    var exerciseFormset = segmentForm.querySelector('.exercise-formset .exercise-list');

    var newExerciseItem = document.createElement('li');
    newExerciseItem.textContent = `Exercise ID: ${document.getElementById('selected-exercise-id').value}, Reps: ${reps}, Duration: ${duration_h}:${duration_m}:${duration_s}, Rest Time: ${rest_time_m}:${rest_time_s}, Notes: ${notes}`;
    exerciseFormset.appendChild(newExerciseItem);

    if (!addNext) {
        document.getElementById('exercise-details-modal').style.display = "none";
    }

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
                    document.getElementById('exercise-details-title').textContent = `${exercise.name} Details`;
                    document.getElementById('exercise-modal').style.display = "none";
                    document.getElementById('exercise-details-modal').style.display = "block";
                };
                exerciseList.appendChild(exerciseItem);
            });
        });
}