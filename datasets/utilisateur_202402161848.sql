INSERT INTO utilisateur (login,email,nom_utilisateur,password,`role`,est_actif) VALUES
	 ('admin','admin@admin.fr','Administrateur','pbkdf2:sha256:600000$828ij7RCZN24IWfq$3dbd14ea15999e9f5e340fe88278a45c1f41901ee6b2f56f320bf1fa6adb933d','ROLE_admin',1),
	 ('client','client@client.fr','Semih Remork','pbkdf2:sha256:600000$ik00jnCw52CsLSlr$9ac8f694a800bca6ee25de2ea2db9e5e0dac3f8b25b47336e8f4ef9b3de189f4','ROLE_client',1),
	 ('client2','client2@client2.fr','Jack Séparou','pbkdf2:sha256:600000$3YgdGN0QUT1jjZVN$baa9787abd4decedc328ed56d86939ce816c756ff6d94f4e4191ffc9bf357348','ROLE_client',1);
