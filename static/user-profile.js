let followForm = document.getElementById("follow-form");
let profileHeading = document.getElementById("username-heading");
let username = profileHeading.innerText;
let currUser = profileHeading.getAttribute("data-curr-user");
let followersBtn = document.getElementById("followers-btn");
let followingBtn = document.getElementById("following-btn");

async function handleFollowForm(e){
    e.preventDefault();
    let response = await axios.post(`/api/follows/${username}`, {"curr_user": currUser});
    window.location.reload();
}

function handleFollowersQuery(e){
    e.preventDefault();
    let target = e.target;
    let username = target.getAttribute("data-username");
    window.open(`/user/followers/${username}`, height=500, width =500);

}

function handleFollowingQuery(e){
    e.preventDefault();
    let target = e.target;
    let username = target.getAttribute("data-username");
    window.open(`/user/following/${username}`, height=500, width =500);

}

if(followForm) followForm.addEventListener("submit", handleFollowForm);
followersBtn.addEventListener("click", handleFollowersQuery);
followingBtn.addEventListener("click", handleFollowingQuery);

