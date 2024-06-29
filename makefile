all:
	@echo "choose a target for make:"
	@echo "-> determinize, minimize, conversion, first_follow or ll1,"
	@echo "or a test target:"
	@echo "-> determinize-test, minimize-test, conversion-test,"
	@echo "-> first_follow-test or ll1-test"
	@echo "or compare the results of the tests using 'make compare'"

determinize:
	@python3 determinization.py

minimize:
	@python3 minimization.py

determinize-test:
	@(python3 determinization.py < tests/test.txt) > tests/test_results.txt
	@cat tests/test_results.txt

minimize-test:
	@(python3 minimization.py < tests/test.txt) > tests/test_results.txt
	@cat tests/test_results.txt

conversion:
	@python3 ER_DFA_conversion.py

conversion-test:
	@python3 ER_DFA_conversion.py < tests/test.txt > tests/test_results.txt
	@cat tests/test_results.txt

first_follow:
	@python3 first_follow.py

first_follow-test:
	@python3 first_follow.py < tests/test.txt > tests/test_results.txt
	@cat tests/test_results.txt

ll1:
	@python3 ll1.py

ll1-test:
	@python3 ll1.py < tests/test.txt > tests/test_results.txt
	@cat tests/test_results.txt

compare:
	@cat tests/test_results.txt tests/test_answers.txt | sort | uniq -u
