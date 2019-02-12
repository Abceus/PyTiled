<?xml version="1.0" encoding="UTF-8"?>
<tileset name="function" tilewidth="16" tileheight="16" tilecount="210" columns="14">
 <grid orientation="orthogonal" width="8" height="8"/>
 <image source="../../../data/images/Arcade - Pac-Man - General Sprites.png" width="225" height="248"/>
 <tile id="0">
  <animation>
   <frame tileid="0" duration="100"/>
   <frame tileid="1" duration="100"/>
   <frame tileid="2" duration="100"/>
  </animation>
 </tile>
 <tile id="1">
  <properties>
   <property name="class_" value="Pacman"/>
   <property name="group" value="player"/>
  </properties>
 </tile>
 <tile id="56">
  <properties>
   <property name="class_" value="Blinky"/>
   <property name="group" value="ghost"/>
  </properties>
 </tile>
 <tile id="70">
  <properties>
   <property name="class_" value="Pinky"/>
   <property name="group" value="ghost"/>
  </properties>
 </tile>
 <tile id="84">
  <properties>
   <property name="class_" value="Inky"/>
   <property name="group" value="ghost"/>
  </properties>
 </tile>
 <tile id="98">
  <properties>
   <property name="class_" value="Clyde"/>
   <property name="group" value="ghost"/>
  </properties>
 </tile>
</tileset>
