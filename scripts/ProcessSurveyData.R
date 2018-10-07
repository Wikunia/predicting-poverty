## PROCESS LSMS DATA##

#### Preliminaries: Load packages, create new folders, define aggregation functions ####
setwd('predicting-poverty') # Set working directory to where you downloaded the replication folder
rm(list=ls())
library(magrittr)
library(foreign)
library(raster)
extract <- raster::extract # Ensure the 'magrittr' package does not mask the 'raster' package's 'extract' function
library(readstata13) # One Tanzanian LSMS .dta file was saved in Stata-13 format
library(plyr)
'%&%' <- function(x,y)paste0(x,y)


dir.create('data/output/LSMS', showWarnings = F)

# Assign each cluster the mean nightlights values over a 10 km^2 area centered on its provided coordinates
nl <- function(df, year){
  # ls.filter identifies the nine clusters we filtered out because of LandScan data availability in our analysis
  ls.filter <- c(0.112190, -1.542321, -1.629748, -1.741995, -1.846039, -1.896059, -2.371342, -2.385341, -2.446988)
  nl <- raster(paste0('data/input/Nightlights/', year, '/', list.files(paste0('data/input/Nightlights/', year))))
  df2 <- subset(df, is.na(lat)==F & is.na(lon)==F & lat !=0 & lon != 0)
  df2 <- unique(df2[,c('lat', 'lon')])
  shape <- extent(c(range(c(df2$lon-0.5, df2$lon+0.5)),
                    range(c(df2$lat-0.5, df2$lat+0.5))))
  nl <- crop(nl, shape)
  for (i in 1:nrow(df2)){
    lat <- sort(c(df2$lat[i] - (180/pi)*(5000/6378137), df2$lat[i] + (180/pi)*(5000/6378137)))
    lon <- sort(c(df2$lon[i] - (180/pi)*(5000/6378137)/cos(df2$lat[i]), df2$lon[i] + (180/pi)*(5000/6378137)/cos(df2$lat[i])))
    ext <- extent(lon, lat)
    nl.vals <- unlist(extract(nl, ext))
    nl.vals[nl.vals==255] <- NULL
    df2$nl[i] <- mean(nl.vals, na.rm = T)
    # Add a column to indicate whether cluster was one of the nine filtered out by LandScan data availability for our study
    # This allows full replication of our data by subsetting survey data to sample == 1 as well as testing on the full survey sample
    # Ultimately, our sample differs from the full sample by just one cluster in Uganda and one in Tanzania
    df2$sample[i] <- if (round(df2$lat[i], 6) %in% ls.filter) 0 else 1
  }
  df <- merge(na.omit(df2), df, by = c('lat', 'lon'))
  return(df)
}

# Aggregate household-level data to cluster level
cluster <- function(df){
  # Record how many households comprise each cluster
  for (i in 1:nrow(df)){
    sub <- subset(df, lat == df$lat[i] & lon == df$lon[i])
    df$n[i] <- nrow(sub)
  }
  # Clustering for LSMS survey data
  ddply(df, .(lat, lon), summarise,
        cons = mean(cons),
        nl = mean(nl),
        n = mean(n),
        sample = min(sample))
  return(df)
}

#### Write LSMS Data ####

## Malawi ##
mwi13.cons <- read.dta('data/input/LSMS/MWI_2016_IHS-IV_v02_M_Stata/IHS4 Consumption Aggregate.dta') %$%
  data.frame(hhid = case_id, cons = rexpagg/(365*adulteq), weight = hh_wgt, expagg = expagg)
mwi13.cons$cons <- mwi13.cons$cons*107.62/(116.28*166.12)
mwi13.geo <- read.dta('data/input/LSMS/MWI_2016_IHS-IV_v02_M_Stata/HouseholdGeovariables_stata11/HouseholdGeovariablesIHS4.dta')
mwi13.coords <- data.frame(hhid = mwi13.geo$case_id, lat = mwi13.geo$lat_modified, lon = mwi13.geo$lon_modified)
mwi13.hha <- read.dta('data/input/LSMS/MWI_2016_IHS-IV_v02_M_Stata/HH_MOD_A_FILT.dta')
mwi13.rururb <- data.frame(hhid = mwi13.hha$case_id, rururb = mwi13.hha$reside, stringsAsFactors = F)
mwi13.hhf <- read.dta('data/input/LSMS/MWI_2016_IHS-IV_v02_M_Stata/HH_MOD_F.dta')
mwi13.room <- data.frame(hhid = mwi13.hhf$case_id, room = mwi13.hhf$hh_f10)
mwi13.metal <- data.frame(hhid = mwi13.hhf$case_id, metal = mwi13.hhf$hh_f10=='IRON SHEETS')

mwi13.vars <- list(mwi13.cons, mwi13.coords, mwi13.rururb, mwi13.room, mwi13.metal) %>%
  Reduce(function(x, y) merge(x, y, by = 'hhid'), .) %>%
  nl(2013)

write.table(mwi13.vars, 'data/output/LSMS/Malawi 2016 LSMS (Household).txt', row.names = F)
write.table(cluster(mwi13.vars), 'data/output/LSMS/Malawi 2016 LSMS (Cluster).txt', row.names = F)

