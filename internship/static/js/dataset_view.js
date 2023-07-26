console.log('ola')
document.getElementById('upload-dataset').addEventListener('change', function (event) {
    const files = event.target.files;
    const maxFilesAllowed = parseInt(event.target.getAttribute('data-max-files'));

    if (files.length > maxFilesAllowed) {
        alert(`You can upload a maximum of ${maxFilesAllowed} datasets.`);
        // Clear the selected files to prevent uploading more than the limit
        this.value = null;
        return;
    }

    // Create a FormData object to send the selected files to the Django view
    const formData = new FormData();
    for (const file of files) {
        formData.append('dataset_files', file);
    }

    // Make an AJAX request to the Django backend
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload_datasets/'); // Replace '/upload_datasets/' with the URL of your Django view that handles the dataset upload

    xhr.onload = function () {
        if (xhr.status === 200) {
            // Request successful, do something with the response if needed
            console.log(xhr.responseText);
        } else {
            // Request failed, handle the error
            console.error('Error uploading datasets:', xhr.status, xhr.statusText);
        }
    };
    xhr.onerror = function () {
        // Error handling for network errors
        console.error('Network error occurred while uploading datasets');
    };

    // Send the FormData with the selected files to the Django view
    xhr.send(formData);
});
