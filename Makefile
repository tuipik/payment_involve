build:
	@docker build -t tuipik/payment_involve:latest .
pull:
	@docker pull tuipik/payment_involve:latest
run:
	@docker-compose up
test:
	@docker-compose run app sh -c "pytest"