"use client";

import ContactButton from "@/components/ContactButton";
import ProfileMenu from "@/components/ProfileMenu";
import { Grid, GridItem, Flex, Box } from "@chakra-ui/react";

export default function App() {
  return (
    <Grid templateColumns="0.5fr 4fr" height="100vh">
      <GridItem borderWidth="2px" borderColor="gray.700" p="1px">
        <Flex
          direction="column"
          height="100%"
          borderRight="1px"
          borderColor="gray.500"
        >
          <ContactButton
            avatar="https://i.pravatar.cc/300"
            number={123123123}
            ID="XD"
          />
          <ContactButton
            avatar="https://i.pravatar.cc/300"
            number={123123123}
            ID="XD"
          />
          <ContactButton
            avatar="https://i.pravatar.cc/300"
            number={123123123}
            ID="XD"
          />
          <Box marginTop="auto">
            <ProfileMenu
              avatar="https://i.pravatar.cc/300"
              number={123123123}
            />
          </Box>
        </Flex>
      </GridItem>
      <GridItem>
        <p>Hey</p>
      </GridItem>
    </Grid>
  );
}
