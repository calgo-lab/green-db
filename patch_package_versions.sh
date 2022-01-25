for VARIABLE in "core" "database" "extract" "message-queue" "scraping" "workers"
do
	cd $VARIABLE
	echo "Package:" $VARIABLE
	poetry version patch
	echo
    cd ..
done
