import { Grid, GridItem, Text, Avatar, Flex } from "@chakra-ui/react";
import React from "react";

function ProfileMenu({ avatar, number }: { avatar: string; number: number }) {
  return (
    <Grid
      templateColumns="1fr 4fr"
      minHeight="50px"
      maxHeight="60px"
      bg="blue.400"
      margin="0.5vh 0 0 0"
      cursor="pointer"
    >
      <Flex justify="center" align="center">
        <GridItem p="5% 0" paddingLeft="1vw">
          <Avatar.Root size="md">
            <Avatar.Fallback name={`${number}`} />
            <Avatar.Image src={avatar} />
          </Avatar.Root>
        </GridItem>
        <GridItem p="0 1vw">
          <Text textStyle="xl">{`${number}`}</Text>
        </GridItem>
      </Flex>
    </Grid>
  );
}

export default ProfileMenu;
