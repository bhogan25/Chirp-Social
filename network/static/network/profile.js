document.addEventListener('DOMContentLoaded', function() {

  document.querySelector('#followUnfollowButton').onclick = followOrUnfollow;
})


function followOrUnfollow(event) {
  event.preventDefault();
  
  const profile_username = document.querySelector('#profileUsername').innerHTML;
  let followUnfollowButton = document.querySelector('#followUnfollowButton');
  const followersCountElement = document.querySelector('#followersCount');
  let count = Number(followersCountElement.innerHTML);

  if (followUnfollowButton.innerHTML == "Follow") {

    // PUT request to Follow User

    fetch('/follow', {
      method: 'PUT', 
      body: JSON.stringify({
        action: 'follow',
        target_username: profile_username
      })
    })
    .then(reponse => reponse.json())
    .then(data => {
      if (!data.error) {
        console.log(data.message)
        count++;
        followersCount.innerHTML = count;
        followUnfollowButton.innerHTML = 'Unfollow';
      } else {
        console.log('Request unsuccessfull');
        alert(`Request unseccessfull: ${data.error}`);
      }
    })
    .catch(error => {
      console.log(error)
      alert(`Unable to complete request. ${error}`)
    })

  } else if (followUnfollowButton.innerHTML == "Unfollow") {

    // DELETE request to Follow User

    fetch('/follow', {
      method: 'DELETE', 
      body: JSON.stringify({
        action: 'unfollow',
        target_username: profile_username
      })
    })
    .then(reponse => reponse.json())
    .then(data => {
      if (!data.error) {
        console.log(data.message)
        count--;
        followersCount.innerHTML = count;
        followUnfollowButton.innerHTML = 'Follow';
      } else {
        console.log('Request unsuccessfull');
        alert(`Request unsuccessfull: ${data.error}`);
      }
    })
    .catch(error => {
      console.log(error)
      alert(`Unable to complete request. ${error}`)
    })

  }
}

