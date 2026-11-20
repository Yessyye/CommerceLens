# Upload package manifest — 2026-11-20

Current local upload payload, based on public main commit `d60bbb4074199b71f5c2a272680c235f9a13e974`.

Includes rewritten English/Chinese documentation, seven actual UI screenshots, unchanged runtime/fixtures and three restored configuration files. Packaged A/B/C offline AppTest passed with the existing Python 3.11.9 environment. No new clean install, live API or Docker benchmark is claimed. No remote action was performed.

`GITHUB_RELEASE_AUDIT.md`, `PUBLICATION_PREVIEW.md` and earlier audit JSON describe previous release candidates. Current packaging results are in [docs/packaging_validation.json](docs/packaging_validation.json); current replay observations are in [docs/packaged_replay_validation.json](docs/packaged_replay_validation.json).

Root LICENSE covers project-owned code/docs; vendor and Olist-derived fixtures retain their separate notices. Olist-derived data is for noncommercial demonstration under its data license.

Excluded: .git, real .env, raw CSV, DuckDB, virtual environments, caches and nested ZIP archives. ZIP paths start directly at README.md/scripts/docs, without an extra project directory.

SHA-256 below covers all payload files except this manifest.

| File | Bytes | SHA-256 |
|---|---:|---|
| .env.example | 65 | 6e6ac3f072c4b9dc756ba876cbde0a78660617cf425d5c1d82caff5b448051b8 |
| .gitignore | 2399 | 2b11be18bbf93c4f6e51154e779eee716d32f0e95b1ffe364d456ccfd76203fc |
| .streamlit/config.toml | 192 | 333ec0933e99f850b7e5ea624d15d3c87680e94421936d828a66da6313d3835f |
| artifacts/phase1/query_results.json | 3783 | 4ad6f106fe531e97da79b345afed4154276ac90cb4654bbe05c37bff02d50815 |
| artifacts/phase2/planner_0bae01c8d97e481fad990a5ace79cc9f.json | 4856 | df78d079a3baeec1f55873d807423adc0ced817b1a784b1e4a7df9b2a9f77653 |
| artifacts/phase2/planner_0e9104dbfdb046ecae6172273ea25bfe.json | 2836 | de06e0482972c043c6658b66b7bd284482ad1c1fe4e953216ee6f68f376d00b9 |
| artifacts/phase2/planner_1db99daf59ed4cdab7a7169627baa66b.json | 10176 | 8ab7e6f7d890b23321e2057b4d114924d6f58b9e7c9aa00ae6583138f486637f |
| artifacts/phase2/planner_213a42097d2e4fdfbce177f6874213a2.json | 2994 | 6b20a997e36ed612f7fa61027a1d15f7177bfabeb548fde04e33f408fabda041 |
| artifacts/phase2/planner_29aacd7933574c2b87234d08465a3938.json | 5052 | 763d848690bf1b5630948e1bb85382fdffb10a7ffe38076029902632bd04d5ca |
| artifacts/phase2/planner_2b936e75a12a43149c1e4783393c54b6.json | 4907 | a605eac210fd5ad311efb1bffbfdb3ad90213aed03cdd569a0c060f69d4f0ee9 |
| artifacts/phase2/planner_2e00f670a79941c29ab6e903ff155521.json | 2880 | c39c77cab8b2da770a05f15acf4979768d88fa66416c7e2f01a9327d583dc8eb |
| artifacts/phase2/planner_42952277a5b84566941527b51627d4e6.json | 6704 | fc34df14cd40fd9b6ab0a25456e276883bdf725d19bab3d230d251e699c6ee79 |
| artifacts/phase2/planner_5118329795904bb199277a94d7bf9dfb.json | 3327 | 6805c6fa0cc6a60a6e82b0443dca63fdfa7a5d1b7ef409d70f67fcbf79fdc28a |
| artifacts/phase2/planner_5dd3ef11531341d1bf6b9764f11fbacf.json | 3060 | b206de6fabc173498a6412cd894eea8f6a5d97be5e3c56e201cec6dc7a9ffc2c |
| artifacts/phase2/planner_5efc6da699ed450a961cc6b69d698311.json | 3467 | 63e24de87454f54d15ba216a98dc41338bde0ba3d1c7283ed244d7b2cd088e9a |
| artifacts/phase2/planner_7193e332077049e0be6b11175b0ec735.json | 10536 | 25b48547940021be685e6335285a4ce9bfbb82fa56375614538216c12d88a45f |
| artifacts/phase2/planner_828c29afcf564eeca3c475c9dd5871d2.json | 5435 | 7b32a08cb5b95111a0e138dfc7e8b1a41371bcdedbc0fc514c47dd703a9ffbcc |
| artifacts/phase2/planner_9390a70cdbb44314a828541de78981d5.json | 3143 | 72281d1ffdc47e70f27fb9e41929769b2eb4f50dc75c468eab95745598824b01 |
| artifacts/phase2/planner_98bc24e5e9ba47a5832de4944ea247b5.json | 2773 | b3e5c97e3cd09e0abdfa121fbbedb885d167e41dd88267cbf4a32a24004887f0 |
| artifacts/phase2/planner_99277b0309204334bda77f6f99f55583.json | 3601 | d69e850b737d727f3d803126188936ff49dadcea916dea21c1426c039055a84e |
| artifacts/phase2/planner_b15b435f72ab4f5a99bf390c2da480c0.json | 11007 | ea5bab5ab4599272b1683b6c5cc5380129c2fea00ac871ccea8ffbd2b5672dfe |
| artifacts/phase2/planner_b3d7b583c8df4fd783b9e75da035efd8.json | 3451 | 161abed1dc86030523ef26bd77e5295de479e7ae5544783048576ffe1f670e71 |
| artifacts/phase2/planner_bb1a3a183ff541b4a3c0f865cd6a6c73.json | 10200 | 07620328f81e68876ebe30e7ba100048c52598e13ef9d599b26a748313589d71 |
| artifacts/phase2/planner_d10ed626126f45dd8f5330475909f225.json | 10842 | 564a49c6e3570e231fcaf5cba2c2a227ff769e6bf89a8e6c63ef8063607b7988 |
| artifacts/phase2/planner_df5ee6359026444bb170f7cc32d97f8e.json | 3835 | 3079f99176482934ebbf4ed10034d900cfcbeea7fcf819d52fcfb0cb6f650e68 |
| artifacts/phase2/planner_f1a60a38ef44406dac2d81bfa440b20b.json | 4861 | e9fe81fb806e5cf088d2910f8fe3df3b63cdfda4fbc70cb7ea1831f37e6b86d3 |
| artifacts/phase3/agent_eval.json | 2134 | 320256eb19ba67a7bc1d865c2573bfa9178d41c3751c580438952c5585775665 |
| artifacts/phase3/agent_eval_docker.json | 2289 | 5c6a675efc22dfc5d42df1b991af60e4a09e8a704c825193f44685e1f53a5800 |
| artifacts/phase3/agent_eval_initial.json | 2197 | 7af5efd61d8056bde603954a7fc0f1056c28b09d3ecfb67ab1e098a3d6baed67 |
| artifacts/phase3/bi_comparison_pilot.json | 13110 | f152ce5d861d514a995b959a7ec012702f7a6b761e1b4cb3b6c8831326279b30 |
| artifacts/phase3/diagnostic_eval.json | 12705 | 23bfc05049502fed2277bd3226aa3d5f0c1f3203e3a3e7720245dddad56036a3 |
| artifacts/phase3/diagnostic_fault_checks.json | 397 | 34cb0264d06ab1a523ee36c3742cb0a50ecb90a49b03265e51a6fd8e14f5f861 |
| artifacts/phase3/golden_sql_results.json | 8442 | e849e790debed5576adc63f32bd6e39f92e3ef3ba68832357da40071005a9757 |
| artifacts/phase3/sql_policy_validation.json | 908 | 11fb24a72455c23399311dd4b7b001eed561797959eb094d6a6ccc951d9024b4 |
| commercelens_eval/__init__.py | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| commercelens_eval/agent_eval.py | 4218 | 48fecbacd84ded647e8e2d325ba7c6921166947d004e8f4cf2345608029ec2b7 |
| commercelens_eval/baseline.py | 4855 | 60169ebcdb905ef7342abae0f81688c9a99c1c5bceeb6013a1bf8c942d2b4996 |
| commercelens_eval/diagnostic_eval.py | 5063 | fa0f977d5aff98b0fa5edc651078a6c46998f98e59eae482d04cc00051686c8f |
| commercelens_eval/diagnostic_faults.py | 3672 | eaed3b299b565ee84ac5551abf52f8a0ce74af364385559f6f6f93c918e45033 |
| commercelens_eval/golden_sql.py | 3405 | f91595b4fe4bafe1ae7b8fc4f1ed9e6ec6ebc255dfc8d426bde4f00e9e29fb3e |
| commercelens_eval/question_routing.py | 1897 | 3f35d5816ea57767f7c3866d02f18ccf495f83f46f5593aca426f94737e9a8f5 |
| commercelens_eval/regression.py | 3846 | 0ac8d71357d86882556df430646cbcd5ff56b6fbd8ca95c597e04a6a40aa7994 |
| commercelens_eval/sql_policy.py | 1804 | a00365934012838dae6dcc50673c0fa5b0f0e942b27b3252248ece77d2aefdfc |
| data/README.md | 1194 | 795e4e35719ac09baeaaeaea18637e1fe3a7f32b4913495f9915d860e8dd57d0 |
| DATA_LICENSE.md | 2372 | ecd264506e6a567b4b1a0d5b38344a596e31b3df3f68202a459f48f32426170c |
| docs/architecture.md | 8835 | f2dab89f51cf422f0d95f6fb8e654daa4520fbfd0b81387fb193381c5b709fda |
| docs/assets/demo_case_b.jpg | 61143 | fb67c917aa76dca1762acf4c9744a36699308f2f5d7f7e07cab4b4f4b10c3155 |
| docs/assets/demo_case_c.jpg | 58748 | 5a1f2521270b698f4aaa5767cb48360bbb33b58492da16fa34a649e680c3d932 |
| docs/assets/demo_diagnostic.jpg | 61605 | db49a1fab71fd2f33886bc727dd708562252f3832682051f5f64908321ff0463 |
| docs/assets/demo_evidence_eval.jpg | 47370 | 9ff5dc97152883f3d92918cadae2e2872859236382e8f3afeecb062f706b66ba |
| docs/assets/demo_home.jpg | 45365 | 37f984981d718de74e52b64c0b8554913d82b1814fcae5321f177d2cea60059f |
| docs/assets/demo_overview.jpg | 57996 | 1b118413661ee069c6eeef80c9de703c1f58690546d50be70b0dc17f811472de |
| docs/assets/demo_sql.jpg | 58994 | 5cfe755b9941b83c10f03cfff96d8e49237c1a6c41ed3841ae4537856c7c7ad4 |
| docs/candidate_security_results.json | 354 | ca53e22169762ea57e16f72b2734dbb08f959dc451e4de8a5dea4bec8f14f67e |
| docs/candidate_test_results.json | 1960 | 33a174826950724fdb5d6fce092a3ce8e9f9dde59764199236adbb8e47111407 |
| docs/dependency_licenses.json | 17629 | dd677761275acfbd6228a5469102daebc2a21a3c6636fbb4b82b95dadf86fbc8 |
| docs/derived_data_inventory.md | 9666 | 31a8b3f6e3820552d6722dff7cf22203a76cd0911ec528cf65aaa37d41ccc403 |
| docs/documentation_review.md | 7820 | ff29b2da6b8bb6f16395ea1640838c104ba6332e21eeb00b509b0c82bb251bdb |
| docs/documentation_validation.json | 1999 | 8b41b6faed186101198f9016681fab9cd97b430ad9ed8bc0ad09d7f82eba25d9 |
| docs/evaluation.md | 7295 | 8a5ea642975542ab874ad7cdc0976cd44afebff0592d53805205e92da47f76ac |
| docs/fresh_replay_validation.json | 3270 | 8c27ce9699584eada5e5178664169c1b0d7d037dc17b41b97b8ba83cfc07a72e |
| docs/implementation_map.md | 31367 | b2bba7117535bb6af9aa1d32b8d101a0cd920b4f12f1805f57ce5b73fc85d8c4 |
| docs/packaged_replay_validation.json | 2026 | da6e76652de7aefce9ab7fcf7c03f8f90688ce09e0ab511ee2c450cb4ea79557 |
| docs/packaging_validation.json | 655 | 231a9ba23d4db7232f68ffa85953bf92927ac74d15476a62fb991a8ce306e046 |
| docs/project_structure.md | 4663 | ec35e3a9d3bab74bdd66ee65cb32084fd680a982611f9a841edaa9e0a601a5be |
| docs/source_identity.json | 3739 | 25229901299afb37e9e86786b224eb5bde81709f84b411a74503471ce05b7477 |
| docs/technical_design.md | 11975 | a03dc5c8ef7caa0357a7ceacc2862215ec6adfe8d5cc9846bd418f7e10943758 |
| GITHUB_RELEASE_AUDIT.md | 11848 | 2bccb3c4f063b7474ff98e32c6e330fee39e580145770590a2a11819660d1f5e |
| LICENSE | 1313 | b35cea8e98cecad8067615eff9039395d3c639db5d357f172e5fd47fc8e8dcd1 |
| PUBLICATION_PREVIEW.md | 4982 | a73358608f2c20d6238e8f8798b815110fdf307cc5d559451291c35dd8f7dc6b |
| README.md | 11643 | 10936de1e3ebaf00a7e924ead2a0fcc1171c0c48b0fcf844b773d0eff5acae5f |
| README.zh-CN.md | 10886 | 128fa482b6be328a9c886ec211a243ec0e9464f766ec3cdd2446faacde1f1a39 |
| requirements-demo.txt | 57 | 126ec0a030162a0df296fc45a36362439439a80ce942dce2ec6a505a1e2350a7 |
| requirements-phase0.lock | 1349 | d9dce3d1e942dccbac8afed85f326798020299d7685f26175a22d18824b554f7 |
| requirements-replay.txt | 19 | 455666b14a451b140fb905e25133ee20eaa6b544dcb73e48b278719cac4461a2 |
| scripts/analysis_periods.py | 4303 | 90d89624ce78bc2a185f7b79d59fcaa89cda5205078d1ba90d08ea53a13b20e3 |
| scripts/analyst_adapter.py | 4992 | 4d891398c8bfd3af00b9897f0d9685b602139db85a965a6a3ece7cff539391be |
| scripts/build_phase1_data.py | 2329 | 1f57641de6912562a53a02c0746661b088591585cf4ae4890792bc42158629c8 |
| scripts/business_questions.py | 3440 | 4ade784832d5c91f86850a7b442e402896b7cd648eb9abdbb68a1d93dfea1c3e |
| scripts/check_phase1_mcp.py | 2938 | 3a891a61e2656c90da6e46eb8c7fe71ec93621b75c699e1fad1955af2714ac3c |
| scripts/check_release_readiness.ps1 | 1122 | 97ec84ffcf1d4a9c5bffb5b04aee4d1688d03faec0f401e377d0c83cb41d1ec9 |
| scripts/demo_app.py | 22281 | 2b9f759a4f139268a6cf40f85539a7a28603ef5d86933d6b1cf4ada8eb8c8b73 |
| scripts/demo_theme.css | 2997 | c37b94d147620e5d41250933f0b3cb2af1b6dc23b988087c953a0e69193be7cf |
| scripts/diagnostic_report.py | 3226 | f9cc3571418dc536d7938c2ce117b18ed7f7cf639bf73217cc5bdadb5f8ee4a2 |
| scripts/docker_review.py | 4644 | cded438f4b3cb2aef97a3424a29acaf1ed9a85cee29933804d55bcda570de913 |
| scripts/phase1_mcp.py | 3480 | 752f26efe2e10ad1c75ba4f84402c0a82c88ee5f0e4bc2c0cd904fb5beccd420 |
| scripts/phase1_metrics.yaml | 1075 | f991d25cc8e9c6c582a4c9f509861b36d5db6f142fddfb4e1b2d2d3076f442de |
| scripts/phase2_planner.py | 13937 | 82ee3909354df2d3b9c2e0a6eca9b0070da915feb04e297a3350994db6e5bfb2 |
| scripts/sales_drivers.py | 983 | dcce6c3b1463038225b6d66fbf6dc293cb457494ca4aab579ac3789690e995ba |
| scripts/start_demo.ps1 | 445 | 65c440cb1c102106d756cf17ff8c096a396c72ca8e0b5c2abb24de24e71d4eff |
| THIRD_PARTY_NOTICES.md | 2917 | 2ccb825484f9af937293bb0d572b16ebf47046456306264c16936d7ae3114b1d |
| vendor/DeepAnalyze/demo/chat_v2/backend_app/services/__init__.py | 2 | 7eb70257593da06f682a3ddda54a9d260d4fc514f645237f5ca74b08f8da61a6 |
| vendor/DeepAnalyze/demo/chat_v2/backend_app/services/docker_executor.py | 23977 | b6aec352ae968cb636f12b0ab5c6cdb9966bb009e5ea013ab915e0a7ff3a7cda |
| vendor/DeepAnalyze/demo/chat_v2/backend_app/services/sample_catalog.py | 2682 | 68b8ad45f14e7bd7841904ac8e0b5952ddb90794b97527c55a14caf37293a990 |
| vendor/DeepAnalyze/demo/chat_v2/backend_app/services/workspace.py | 34975 | 3c6e1223475908469caed91ad852d02e8107390113ead9f671e9ae019803a0ab |
| vendor/DeepAnalyze/demo/chat_v2/backend_app/settings.py | 6420 | 84926361da8153e70fcb0e4d850c4ff870573bdc20a87c9ca8050894b7200e37 |
| vendor/DeepAnalyze/LICENSE | 1089 | 0284994b204630df23a1c8bfc9d8f69a779eabe8e3771fac88dbdd3b345b94c1 |
