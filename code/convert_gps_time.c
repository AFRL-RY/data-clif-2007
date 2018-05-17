// pos file from 20091021 frame 100
// gps_seconds = 332717.087305
// gps_week = 1554
// 
// time_between_seconds is the constant between Unix epoch and GPS epoch
// time_between_seconds is the number of seconds between 1/6/1980 - 1/1/1970 which is 315964800.0
// leapOffset is the number of seconds that has been added to UTC for leap seconds
//      since (2013) the leap offset is 16 seconds
//		the leap offset was not included in the original date calculations for the CLIF data
//
// This code is designed for a unix system (such as Linux and/or macOS)
#include <stdio.h>
#include <time.h>

void convertGPSTime(double gps_seconds, double gps_week, struct tm *gmt) {
	double imu_time;
	double leapOffset = -1;
	time_t imu_time_t;

	const double time_between_seconds = 315964800.0;
	double gps_weekSeconds = gps_week * 7 * 24 * 3600;
	imu_time = time_between_seconds + gps_seconds + gps_weekSeconds - leapOffset;
	imu_time_t = (time_t) imu_time;
	gmt = gmtime(&imu_time_t);

	year = 1900 + gmt->tm_year;
	month = gmt->tm_mon + 1;
	day_of_month = gmt->tm_mday;
	hour = gmt->tm_hour;
	minute = gmt->tm_min;
	second = gmt->tm_sec;
	printf("date: %04d/%02d/%02d time: %02d:%02d:%02d\n");
}