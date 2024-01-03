// Import necessary modules and initialize posts array
const express = require('express');
const router = express.Router();

let posts = [];

// Home Page - View All Posts
router.get('/', (req, res) => {
  res.render('index', { posts });
});

// Post Creation
router.post('/create', (req, res) => {
  const { title, content } = req.body;
  const newPost = { title, content };
  posts.push(newPost);
  res.redirect('/');
});

// Post Editing
router.get('/edit/:id', (req, res) => {
  const postId = req.params.id;
  const postToEdit = posts[postId];
  res.render('edit', { postToEdit, postId });
});

router.post('/edit/:id', (req, res) => {
  const postId = req.params.id;
  const { title, content } = req.body;
  posts[postId] = { title, content };
  res.redirect('/');
});

// Post Deletion
router.get('/delete/:id', (req, res) => {
  const postId = req.params.id;
  posts.splice(postId, 1);
  res.redirect('/');
});

module.exports = router;
