<?php
require 'db.php';

/* CREATE */
if (isset($_POST['submit'])) {
    $stmt = $pdo->prepare("INSERT INTO users (name, email) VALUES (?, ?)");
    $stmt->execute([$_POST['name'], $_POST['email']]);
    header("Location: index.php");
}

/* READ */
$users = $pdo->query("SELECT * FROM users ORDER BY id DESC")->fetchAll();
?>

<!DOCTYPE html>
<html>
<head>
    <title>PHP CRUD MariaDB</title>
</head>
<body>

<h2>Add User</h2>
<form method="post">
    <input type="text" name="name" placeholder="Name" required>
    <input type="email" name="email" placeholder="Email" required>
    <button name="submit">Save</button>
</form>

<h2>User List</h2>
<table border="1" cellpadding="5">
<tr>
    <th>ID</th><th>Name</th><th>Email</th><th>Action</th>
</tr>

<?php foreach ($users as $user): ?>
<tr>
    <td><?= $user['id'] ?></td>
    <td><?= $user['name'] ?></td>
    <td><?= $user['email'] ?></td>
    <td>
        <a href="edit.php?id=<?= $user['id'] ?>">Edit</a> |
        <a href="delete.php?id=<?= $user['id'] ?>" onclick="return confirm('Delete?')">Delete</a>
    </td>
</tr>
<?php endforeach; ?>

</table>
</body>
</html>
