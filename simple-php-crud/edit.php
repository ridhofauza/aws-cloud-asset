<?php
require 'db.php';

$id = $_GET['id'];

/* FETCH DATA */
$stmt = $pdo->prepare("SELECT * FROM users WHERE id=?");
$stmt->execute([$id]);
$user = $stmt->fetch();

/* UPDATE */
if (isset($_POST['update'])) {
    $stmt = $pdo->prepare("UPDATE users SET name=?, email=? WHERE id=?");
    $stmt->execute([$_POST['name'], $_POST['email'], $id]);
    header("Location: index.php");
}
?>

<form method="post">
    <input type="text" name="name" value="<?= $user['name'] ?>" required>
    <input type="email" name="email" value="<?= $user['email'] ?>" required>
    <button name="update">Update</button>
</form>
