require(latticeExtra)
require(png)

plot_trial <- function(path, trial) {
  log <- paste(path,sprintf("trial-%02d.txt", trial),sep="/")
  img <- paste(path,sprintf("trial-%02d.png", trial),sep="/")
  d <- subset(read.delim(log), state=="SEARCH")
  rimg <- readPNG(img, FALSE)
  p1 <- xyplot(smi_syl~smi_sxr,data=subset(d, event_type=="ET_SPL" & smi_dyl!=0),
               col="blue", type="b", aspect=1050/1680, ylim=c(0,1050), xlim=c(0,1680),
               panel=function(...) {
                 grid.raster(as.raster(rimg))
                 panel.xyplot(...)
               })
  p1 <- p1 + xyplot(smi_fy~smi_fx,data=subset(d, smi_type=="r"), col="red", aspect=1050/1680, ylim=c(0,1050), xlim=c(0,1680))
  p1 <- p1 + xyplot(mouse_y~mouse_x,data=subset(d, event_id=="MOUSE_MOTION" | event_id=="MOUSE_RESET"), type="b", col="green", aspect=1050/1680, ylim=c(0,1050), xlim=c(0,1680))
  print(p1)
}