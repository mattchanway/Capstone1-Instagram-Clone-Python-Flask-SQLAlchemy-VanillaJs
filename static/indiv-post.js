let commentForm = document.getElementById("add-comment-form");
let postId = document.getElementById("post-frame").getAttribute('data-postid');
let commentList = document.getElementById("comment-list");
let postLikeIcon = document.getElementById("post-like-icon");

let currUser =  commentList.getAttribute("data-curr-user");
let currUserId =  postLikeIcon.getAttribute("data-curr-userid");
let likersLink = document.getElementById("likers-link");
let deleteButton = document.getElementById("post-delete-btn");

// async function handlePostDelete(e){
//     e.preventDefault();
//     let target = e.target;
//     let postId = target.getAttribute("data-postid");
//     let response = await axios.post(`/api/posts/${postId}`);
//     window.open(`http://127.0.0.1:5000/`);


// }

async function handleAddCommentForm(e){
    let commentText =  document.getElementById("added-comment").value;
    let newComment = {"comment": `${commentText}`}
    e.preventDefault();
    let response = await axios.post(`/api/comments/add/${postId}`, newComment);
    window.location.reload();
}

async function handleDeleteCommentForm(commentId){
    
    let response = await axios.post(`/api/comments/${commentId}`)
    window.location.reload();

}

async function handleCommentLikeUnlike(commentId){

    let response = await axios.post(`/api/commentlikes/${commentId}`, {"curr_user": currUser})
    window.location.reload();
}

async function handlePostLikeUnlike(e){
    let target = e.target;
    let postId = target.getAttribute("data-postid");

    let response = await axios.post(`/api/posts/likes/${postId}`, {"curr_userid": currUserId})
    window.location.reload();
}

 function handlePostLikersQuery(e){
    e.preventDefault();
    let target = e.target;
    let postId = target.getAttribute("data-postid");
    window.open(`/posts/${postId}/likers`, height=500, width =500);

}

function handleCommentLikersQuery(commentId){
    window.open(`/commentlikes/${commentId}`, height=500, width =500);
}


commentList.onclick = function (event){
    event.preventDefault()
    let target = event.target;
    let commentId = target.getAttribute("data-commentid");
    if(target.classList.contains('fa-trash')) {
        commentId = target.parentElement.getAttribute("data-commentid");
        handleDeleteCommentForm(commentId); } 
    if(target.classList.contains('fa-heart')) {
        commentId = target.parentElement.getAttribute("data-commentid");
        handleCommentLikeUnlike(commentId);}
    if(target.tagName == 'A'){ 
        let id = target.parentNode.dataset.commentid;
        console.log(id);
        handleCommentLikersQuery(id);}
};

commentForm.addEventListener("submit", handleAddCommentForm);
postLikeIcon.addEventListener("click", handlePostLikeUnlike);
likersLink.addEventListener("click", handlePostLikersQuery);
// deleteButton.addEventListener("click", handlePostDelete);




