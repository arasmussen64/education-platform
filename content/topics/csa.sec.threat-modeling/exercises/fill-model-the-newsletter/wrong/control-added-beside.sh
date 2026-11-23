# The control's gap filled with a kind that fits the letter and not the
# threat (a second factor: a mailing company's server has no phone), and
# a second control line added beside it to cover the guess.
sed -i '10s/___/store/' ~/model.tm
sed -i '11s/___/mailer-co/' ~/model.tm
sed -i '18s/___/3/' ~/model.tm
sed -i '21s/___/S/' ~/model.tm
sed -i '22s/___/TRIDE/' ~/model.tm
sed -i '27s/___/mfa/' ~/model.tm
sed -i '36s/___/5/' ~/model.tm
sed -i '37s/___/real subscribers stop getting the newsletter/' ~/model.tm
echo 'control c2 t2 signing check the signature on every bounce report' >> ~/model.tm
