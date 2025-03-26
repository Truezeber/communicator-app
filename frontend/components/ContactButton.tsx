import { Avatar, Flex, Grid, GridItem, Text } from "@chakra-ui/react";

const ContactButton = ({
  avatar,
  number,
  ID,
}: {
  avatar: string;
  number: number;
  ID: string;
}) => {
  return (
    <Grid
      templateColumns="1fr 4fr"
      minHeight="50px"
      maxHeight="60px"
      bg="green.400"
      margin="0.5vh 0 0.5vh 0"
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
};

export default ContactButton;
