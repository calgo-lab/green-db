for VARIABLE in "core" "database" "extract" "message-queue" "scraping" "workers"
do
	cd $VARIABLE
	echo "Package:" $VARIABLE
	poetry version patch
	echo
    cd ..
done

echo "Do not forget to update the helm charts!!"
echo "\t1. infrastructure/charts/scrapyd/Chart.yaml"
echo "\t2. infrastructure/charts/worker/Chart.yaml"
echo
echo "... And finally create and push a git tag."