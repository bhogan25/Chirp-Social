document.addEventListener('DOMContentLoaded', function() {

  // Like Button Event Listeners
  const likeUnlikeButtons = document.querySelectorAll('.like-unlike-button');

  for (let i = 0; i < likeUnlikeButtons.length; i++) {
    likeUnlikeButtons[i].onclick = likeOrUnlike;
  }

  // Edit Button Event Listeners
  const postContentEditButtons = document.querySelectorAll('.edit-button');

  for (let i = 0; i < postContentEditButtons.length; i++) {
    // Get post id
    postId = postContentEditButtons[i].id.split('_').pop();
    
    // Add Event Listener to Save Button
    document.querySelector(`#postContentSaveButton_${postId}`).onclick = editPost;

    // Edit/Cancel Button Event
    postContentEditButtons[i].onclick = function(event) {
      // event.target is 'Edit' button
      event.preventDefault;

      // Get post id and corresponding post elements
      const postId = event.target.id.split('_').pop();
      const textarea = document.querySelector(`#postContentEdit_${postId}`);
      const saveButton = document.querySelector(`#postContentSaveButton_${postId}`);
      const content = document.querySelector(`#postContent_${postId}`);

      if (event.target.innerHTML == "Edit") {
        // Set textarea value to content value
        textarea.value = content.innerHTML;

        // Edit Mode: Show textarea and save button, hide content
        textarea.style.display = "block";
        saveButton.style.display = "inline";
        content.style.display = "none";
        event.target.innerHTML = "Cancel";

      } else if (event.target.innerHTML == "Cancel") {
        // Non-Edit Mode: Hide textarea and save button, show content
        textarea.style.display = "none";
        saveButton.style.display = "none";
        content.style.display = "block";
        event.target.innerHTML = "Edit";
      }
    }
  }
})

function likeOrUnlike(event) {
  event.preventDefault();

  // Get post id and HTML elements
  const targetPostId = event.target.id.split("_").pop();
  const likeUnlikeButton = event.target;
  const likeCountElement = document.querySelector(`#likeCount_${targetPostId}`);
  let count = Number(likeCountElement.innerHTML);

  if (likeUnlikeButton.innerHTML == "Like") {
    // PUT request to like Post

    fetch('/like', {
      method: 'PUT',
      body: JSON.stringify({
        action: 'like',
        target_post_id: targetPostId
      })
    })
    .then(response => response.json())
    .then(data => {
      if (!data.error) {
        console.log(data.message);
        count++;
        likeCountElement.innerHTML = count;
        likeUnlikeButton.innerHTML = "Unlike";
      } else {
        console.log('Request unsuccessfull')
        alert(`Request unseccessfull: ${data.error}`);
      }
    })
    .catch(error => {
      console.log(error);
      alert(`Unable to complete request. ${error}`);
    })

  } else if (likeUnlikeButton.innerHTML == "Unlike"){
  // DELETE request to unlike Post
    fetch('/like', {
      method: 'DELETE',
      body: JSON.stringify({
        action: 'unlike',
        target_post_id: targetPostId
      })
    })
    .then(response => response.json())
    .then(data => {
      if (!data.error) {
        console.log(data.message);
        count--;
        likeCountElement.innerHTML = count;
        likeUnlikeButton.innerHTML = "Like"
      } else {
        console.log('Request unsuccessfull')
        alert(`Request unseccessfull: ${data.error}`);
      }
    })
    .catch(error => {
      console.log(error);
      alert(`Unable to complete request. ${error}`);
    })
  }
}


function editPost(event) {
  // event.target is 'Save' button
  event.preventDefault;

  // Get post id and corresponding post elements
  const postId = event.target.id.split('_').pop();
  const textarea = document.querySelector(`#postContentEdit_${postId}`);
  const content = document.querySelector(`#postContent_${postId}`);
  const editCancelButton = document.querySelector(`#postContentEditButton_${postId}`);
  const newContent = textarea.value;

  fetch('/edit', {
    method: 'PATCH',
    body: JSON.stringify({
      action: 'edit',
      target_post_id: postId,
      content: newContent
    })
  })
  .then(response => response.json())
  .then(data => {
    if (!data.error) {
      console.log(data.message);

      // Non-Edit Mode: Hide textarea and save button, show content
      editCancelButton.innerHTML = "Edit";
      textarea.style.display = "none";
      event.target.style.display = "none";
      content.style.display = "block";

      // Update Post Content
      content.innerHTML = newContent;

    } else {
      console.log('Request unsuccessfull')
      alert(`Request unseccessfull: ${data.error}`);
    }
  })
  .catch(error => {
    console.log(error);
    alert(`Unable to complete request. ${error}`);
  })
}