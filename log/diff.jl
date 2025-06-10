const gd = "! git diff --patch-with-stat --no-index -w"
const sh(c::String) = run(`sh -c $c`)
sh("$gd spAll-lite-v6_0_9.txt spAll-lite-v6_1_0.txt > spAll-lite-v6_0_9.v6_1_0.diff")
sh("$gd spAll-lite-v6_1_0.txt spAll-lite-v6_1_1.txt > spAll-lite-v6_1_0.v6_1_1.diff")
sh("$gd spAll-lite-v6_1_1.txt spAll-lite-v6_1_2.txt > spAll-lite-v6_1_1.v6_1_2.diff")
sh("$gd spAll-lite-v6_1_2.txt spAll-lite-v6_1_3.txt > spAll-lite-v6_1_2.v6_1_3.diff")
sh("$gd spAll-lite-v6_1_3.txt spAll-lite-v6_2_0.txt > spAll-lite-v6_1_3.v6_2_0.diff")
sh("$gd spAll-lite-v6_2_0.txt spAll-lite-v6_2_1.txt > spAll-lite-v6_2_0.v6_2_1.diff")

