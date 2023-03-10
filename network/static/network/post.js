document.addEventListener('DOMContentLoaded', function() {

  // Like Button Event Listeners
  const likeUnlikeButtons = document.querySelectorAll('.like-unlike-button');
  
  for (let i = 0; i < likeUnlikeButtons.length; i++) {
    likeUnlikeButtons[i].onclick = likeOrUnlike;
  }
  
  // Edit Button Event Listeners
  const postContentEditButtons = document.querySelectorAll('.post-content-edit-button');
  
  for (let i = 0; i < postContentEditButtons.length; i++) {
    const textarea = postContentEditButtons[i].nextElementSibling
    
    // Save Button Event
    textarea.nextElementSibling.onclick = editPost;

    // Edit/Cancel Button Event
    postContentEditButtons[i].onclick = function(event) {
      event.preventDefault;
      
      // event.target is 'Edit' button
      const textarea = event.target.nextElementSibling;
      const saveButton = textarea.nextElementSibling;
      const content = saveButton.nextElementSibling;

      if (event.target.innerHTML == "Edit") {
        // Edit Mode: Show textarea and save button, hide content
        textarea.style.display = "block";
        saveButton.style.display = "block";
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

  // Get HTML elements and text
  const username = document.querySelector('#username').innerHTML;
  const targetPostId = event.target.id;
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
  event.preventDefault;

  // event.target is 'Save' button
  const textarea = event.target.previousElementSibling;
  const content = event.target.nextElementSibling;
  const editCancelButton = textarea.previousElementSibling;
  const postId = textarea.id.split('_').pop();
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
      event.target.nextElementSibling.innerHTML = newContent;

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