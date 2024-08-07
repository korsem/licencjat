document.addEventListener('DOMContentLoaded', function() {
    // Initialize the first segment to be empty
    var initialSegmentIndex = 0;
    var initialExerciseTableBody = document.querySelector(`#exercise-table-body-${initialSegmentIndex}`);
    if (initialExerciseTableBody) {
        initialExerciseTableBody.innerHTML = '';
    }
});

// Adds a new segment form when the "Add Segment" button is clicked
document.getElementById('add-segment').addEventListener('click', function() {
    var segmentFormset = document.getElementById('segment-formset');
    var newForm = segmentFormset.lastElementChild.cloneNode(true);
    var formIdx = segmentFormset.querySelectorAll('.segment-form').length; // !

    newForm.setAttribute("id", `segment-${formIdx}`);
    const title = newForm.querySelector("h3");
    title.replaceChild(document.createTextNode(`Segment ${formIdx + 1}`), title.firstChild); //!

    // aby można była dodawać ćwiczenia do odróżnionych formsetów
    newForm.setAttribute("id", `segment-${formIdx}`);

    var exerciseTableBody = newForm.querySelector('tbody[id^="exercise-table-body-"]');
    if (exerciseTableBody) {
        exerciseTableBody.id = `exercise-table-body-${formIdx}`;

        // Clear the existing rows in the exercise table body to make it empty
        exerciseTableBody.innerHTML = '';
    }
    console.log(exerciseTableBody)


    console.log(`Adding new segment with index ${formIdx}`);

    // Update form indices for inputs, textareas, and selects
    newForm.querySelectorAll('input, textarea, select').forEach(function(element) {
        var name = element.getAttribute('name');
        if (name) {
            var updatedName = name.replace(/-\d+-/g, `-${formIdx}-`);
            element.setAttribute('name', updatedName);
        }
        var id = element.getAttribute('id');
        if (id !== null) {
            var updatedId = id.replace(/-\d+-/g, `-${formIdx}-`);
            element.setAttribute('id', updatedId);
        }
    });

    // Update button data-segment attributes
    newForm.querySelectorAll('button').forEach(function(button) {
        button.dataset.segment = formIdx;
    });


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
    var rest_time_m = document.getElementById('rest_time_0').value || '00';
    var rest_time_s = document.getElementById('rest_time_1').value || '00';
    var notes = document.getElementById('notes').value;

    // Validate that either reps or duration is filled, but not both
    if ((reps && (duration_h || duration_m || duration_s)) || (!reps && (!duration_h && !duration_m && !duration_s))) {
        console.log(`Reps: ${reps}, Duration: ${duration_h}:${duration_m}:${duration_s}`);

        alert('Either reps or duration must be specified, but not both.');
        return;
    }

    // Set duration fields to '00' if not provided
    duration_m = duration_m.padStart(2, '0') || '00';
    duration_s = duration_s.padStart(2, '0') || '00';

    if (!reps) {
        duration_h = duration_h || '00';
    } else {
        duration_h = '';
        duration_m = '';
        duration_s = '';
    }

    var segmentIndex = document.getElementById('exercise-modal').getAttribute('data-segment');
    console.log(`Saving exercise details for segment ${segmentIndex}`);

    var exerciseTableBodyId = `exercise-table-body-${segmentIndex}`;
    console.log(exerciseTableBodyId)
    var exerciseTableBody = document.getElementById(exerciseTableBodyId)

    if (!exerciseTableBody) {
        console.error('Exercise table body not found');
        return;
    }
    if (!exerciseTableBody) {
        console.error('Exercise table body not found');
        return;
    }

// name zamiast id wykorzystuje
var exerciseIdElement = document.getElementById('selected-exercise-id');
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
    exerciseTableBody.appendChild(newExerciseRow);

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
                    document.getElementById('exercise-details-title').textContent = `${exercise.name}`;
                    document.getElementById('exercise-modal').style.display = "none";
                    document.getElementById('exercise-details-modal').style.display = "block";
                };
                exerciseList.appendChild(exerciseItem);
            });
        });
}

// save workout
document.getElementById('save-workout').addEventListener('click', function(event) {
    event.preventDefault(); // Zapobiegaj domyślnemu zachowaniu przycisku submit

    var workoutForm = document.getElementById('workout-form');
    var segmentForms = document.querySelectorAll('.segment-form');

    console.log("segmentForms: ", segmentForms);
    console.log("workoutForm: ", workoutForm);

    // Przeprowadź walidację pól formularza
    var isValid = true;
    var segmentsWithExercises = 0; // Licznik segmentów z ćwiczeniami

    segmentForms.forEach(function(segmentForm) {
        var restTimeMinutes = segmentForm.querySelector('input[id^="seg_rest_time_"][id$="_0"]').value;
        var restTimeSeconds = segmentForm.querySelector('input[id^="seg_rest_time_"][id$="_1"]').value;
        var reps = segmentForm.querySelector('input[name$="reps"]').value;
        var exerciseRows = segmentForm.querySelectorAll('tbody tr'); // Wiersze z ćwiczeniami w segmencie

        console.log(exerciseRows)

        // Sprawdzaj, czy pola są wypełnione
        if (!reps) {
            isValid = false;
            alert('All required fields must be filled out.');
            return false; // Zatrzymaj iterację, jeśli znaleziono błąd
        }

        // Sprawdzaj, czy segment ma ćwiczenia
        if (exerciseRows.length > 0) {
            segmentsWithExercises++;
        }

        // Loguj liczbę ćwiczeń dla każdego segmentu
        console.log(`Segment ${segmentForm.id} has ${exerciseRows.length} exercises`);
    });

    // Sprawdź, czy przynajmniej jeden segment ma ćwiczenia
    if (segmentsWithExercises === 0) {
        isValid = false;
        alert('There needs to be at least 1 exercise added to at least one segment.');
    }

    if (isValid) {
        console.log('Saving workout unit with number of segments:', segmentForms.length);
        console.log('Number of segments with exercises:', segmentsWithExercises);
        workoutForm.submit();
    }
});
